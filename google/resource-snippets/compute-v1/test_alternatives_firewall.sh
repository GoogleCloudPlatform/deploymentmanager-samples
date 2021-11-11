set -e

# The following variables are expected to be defined before running this script
# PROJECT_ID=[PROJECT_ID]

GREEN_COLOR='\033[0;32m'
RED_COLOR='\033[0;31m'
RESET_COLOR='\033[0m'

provision_using_dm() {
  gcloud deployment-manager deployments create deployment --config firewall.yaml
  gcloud compute firewall-rules describe address-deployment --project=${PROJECT_ID} --format=yaml \
      | sed "s/${PROJECT_ID}/PROJECT/" | sed "s/creationTimestamp: .*/creationTimestamp: TIME/" \
      | sed "s/id: .*/id: ID/" \
      > /tmp/dm.yaml
  gcloud deployment-manager deployments delete deployment -q
}

provision_using_tf() {
  if [[ -z "${GOOGLE_CREDENTIALS}" ]]; then
    # For Compute, the ADC will have sufficient permissions
    echo "Fetching Application Default Credentials for Terraform"
    gcloud auth application-default login
    export GOOGLE_CREDENTIALS=~/.config/gcloud/application_default_credentials.json
  fi

  cp -R alternatives-firewall/tf/ /tmp/firewall_tf_"${PROJECT_ID}"
  pushd /tmp/firewall_tf_"${PROJECT_ID}"
  terraform init
  terraform plan -var="deployment=deployment" -var="project_id=${PROJECT_ID}"
  terraform apply -auto-approve -var="deployment=deployment" -var="project_id=${PROJECT_ID}"
  gcloud compute firewall-rules describe address-deployment --project=${PROJECT_ID} --format=yaml \
      | sed "s/${PROJECT_ID}/PROJECT/" | sed "s/creationTimestamp: .*/creationTimestamp: TIME/" \
      | sed "s/id: .*/id: ID/" \
      > /tmp/tf.yaml
  terraform destroy -auto-approve -var="deployment=deployment" -var="project_id=${PROJECT_ID}"
  popd
  rm -rf /tmp/firewall_tf_${PROJECT_ID}
}

gcloud config set project "${PROJECT_ID}"

if [[ -n $( gcloud auth list --filter=status:ACTIVE --format="value(account)" ) ]]; then
  account_name=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")
  echo "Reusing $account_name user credentials"
else
  gcloud auth login
fi

gcloud services enable compute.googleapis.com
gcloud services enable deploymentmanager.googleapis.com

provision_using_dm
provision_using_tf
# TODO [#652]: Implement provision_using_krm() and call it here.

if [[ -n $(diff /tmp/dm.yaml /tmp/tf.yaml) ]]; then
    echo -e "${RED_COLOR}TF and DM outputs are NOT identical${RESET_COLOR}"
    echo "diff /tmp/dm.yaml /tmp/tf.yaml"
    diff /tmp/dm.yaml /tmp/tf.yaml
    exit 1
else
    echo -e "${GREEN_COLOR}TF and DM outputs are identical${RESET_COLOR}"
fi

# TODO [#652]: Compare KRM and DM outputs.

echo -e "${GREEN_COLOR}Test Success${RESET_COLOR}"
exit 0
