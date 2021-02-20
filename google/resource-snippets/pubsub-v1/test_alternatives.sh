set -e

TF_PROJECT_ID={TF_PROJECT_ID}
KRM_PROJECT_ID={KRM_PROJECT_ID}
DM_PROJECT_ID={DM_PROJECT_ID}


gcloud auth login

# Create DM resources
gcloud config set project $DM_PROJECT_ID
gcloud services enable deploymentmanager.googleapis.com
gcloud deployment-manager deployments create d1 --config pubsub.yaml

# Create Terraform resources
gcloud config set project $TF_PROJECT_ID
gcloud config list --format 'value(core.project)'
terraform init
terraform apply -auto-approve -var="deployment=d1" -var="project_id=${TF_PROJECT_ID}"


# Export DM and TF resources for comparison
gcloud pubsub subscriptions list --filter="labels.goog-dm:d1" --project $DM_PROJECT_ID | sed "s/${DM_PROJECT_ID}/PROJECT/" > dm.yaml

gcloud pubsub subscriptions list --filter=topic:my-pubsub-topic --project $TF_PROJECT_ID | sed "s/${TF_PROJECT_ID}/PROJECT/"  > tf.yaml
gcloud pubsub subscriptions list --filter=topic:my-backup-topic --project $TF_PROJECT_ID | sed "s/${TF_PROJECT_ID}/PROJECT/"  >> tf.yaml


sort tf.yaml > tf.yaml
sort dm.yaml > dm.yaml

if [[ $(diff dm.yaml tf.yaml) ]]; then
    echo "TF and DM outputs are NOT identical"
    exit 1
else
    echo "TF and DM outputs are identical"
fi


exit 0
