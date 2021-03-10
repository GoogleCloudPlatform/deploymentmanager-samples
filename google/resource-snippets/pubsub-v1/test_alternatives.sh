set -e

GREEN_COLOR='\033[0;32m'
RED_COLOR='\033[0;31m'
RESET_COLOR='\033[0m'

provision_using_dm() {
  gcloud deployment-manager deployments create deployment --config pubsub.yaml
  gcloud pubsub subscriptions list --filter="labels.goog-dm:deployment" --project "${PROJECT_ID}" > /tmp/dm.yaml
  gcloud deployment-manager deployments delete deployment -q
}

provision_using_tf() {
  if [[ -z "${GOOGLE_CREDENTIALS}" ]]; then
    # For pub/sub, the ADC will have sufficient permissions
    echo "Fetching Application Default Credentials for Terraform"
    gcloud auth application-default login
    export GOOGLE_CREDENTIALS=~/.config/gcloud/application_default_credentials.json
  fi

  cp -R alternatives/tf/ /tmp/tf_"${PROJECT_ID}"
  pushd /tmp/tf_"${PROJECT_ID}"
  terraform init
  terraform plan -var="deployment=deployment" -var="project_id=${PROJECT_ID}"
  terraform apply -auto-approve -var="deployment=deployment" -var="project_id=${PROJECT_ID}"
  gcloud pubsub subscriptions list --filter="labels.goog-dm:deployment" --project "${PROJECT_ID}" > /tmp/tf.yaml
  terraform destroy -auto-approve -var="deployment=deployment" -var="project_id=${PROJECT_ID}"
  popd
  rm -rf /tmp/tf_${PROJECT_ID}
}

provision_using_krm() {
  cp -R alternatives/krm/ /tmp/krm_${PROJECT_ID}
  pushd /tmp/krm_${PROJECT_ID}
  kpt cfg set . PUBSUB my-pubsub
  kubectl apply -f pubsub.yaml
  kubectl wait --for=condition=Ready --timeout=60s PubSubSubscription --all
  gcloud pubsub subscriptions list --filter="labels.goog-dm:deployment" --project "${PROJECT_ID}" | sed "s/creationTime: .*/creationTime: TIME/" | sed "/cnrm-lease-.*/d" | sed "/managed-by-cnrm.*/d"  > /tmp/krm.yaml
  kubectl delete -f pubsub.yaml
  popd
  rm -rf /tmp/krm_${PROJECT_ID}
}

gcloud config set project "${PROJECT_ID}"

if [[ -n $( gcloud auth list --filter=status:ACTIVE --format="value(account)" ) ]]; then
  account_name=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")
  echo "Reusing $account_name user credentials"
else
  gcloud auth login
fi

gcloud services enable deploymentmanager.googleapis.com
gcloud services enable pubsub.googleapis.com

provision_using_dm
provision_using_tf
provision_using_krm

if [[ -n $(diff /tmp/dm.yaml /tmp/tf.yaml) ]]; then
    echo "${RED_COLOR}TF and DM outputs are NOT identical${RESET_COLOR}"
    echo "diff /tmp/dm.yaml /tmp/tf.yaml"
    diff /tmp/dm.yaml /tmp/tf.yaml
    exit 1
else
    echo "${GREEN_COLOR}TF and DM outputs are identical${RESET_COLOR}"
fi

if [[ -n $(diff /tmp/dm.yaml /tmp/krm.yaml) ]]; then
    echo "${RED_COLOR}KRM and DM outputs are NOT identical${RESET_COLOR}"
    echo "diff /tmp/dm.yaml /tmp/krm.yaml"
    diff /tmp/dm.yaml /tmp/krm.yaml
    exit 1
else
    echo "${GREEN_COLOR}KRM and DM outputs are identical${RESET_COLOR}"
fi

echo "${GREEN_COLOR}Test Success${RESET_COLOR}"
exit 0
