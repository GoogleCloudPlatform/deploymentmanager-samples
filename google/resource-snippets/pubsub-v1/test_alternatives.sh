set -e

TF_PROJECT_ID={TF_PROJECT_ID}
DM_PROJECT_ID={DM_PROJECT_ID}


gcloud auth application-default login
export GOOGLE_APPLICATION_CREDENTIALS=~/.config/gcloud/application_default_credentials.json

# Create DM resources
gcloud config set project $DM_PROJECT_ID
gcloud services enable deploymentmanager.googleapis.com
gcloud deployment-manager deployments create d1 --config pubsub.yaml

# Create Terraform resources
pushd alternatives/tf
gcloud config set project $TF_PROJECT_ID
terraform init
terraform plan -var="deployment=d1" -var="project_id=${TF_PROJECT_ID}"
terraform apply -auto-approve -var="deployment=d1" -var="project_id=${TF_PROJECT_ID}"
popd


# Export DM and TF resources for comparison
gcloud pubsub subscriptions list --filter="labels.goog-dm:d1" --project $DM_PROJECT_ID | sed "s/${DM_PROJECT_ID}/PROJECT/" > /tmp/dm.yaml

gcloud pubsub subscriptions list --filter="labels.goog-dm:d1" --project $TF_PROJECT_ID | sed "s/${TF_PROJECT_ID}/PROJECT/"  > /tmp/tf.yaml


if [[ $(diff /tmp/dm.yaml /tmp/tf.yaml) ]]; then
    echo "TF and DM outputs are NOT identical"
    exit 1
else
    echo "TF and DM outputs are identical"
fi

exit 0
