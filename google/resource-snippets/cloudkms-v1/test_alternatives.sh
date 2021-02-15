set -e

# assumes that the following projects are created and kubectl context is set to a cluster in KRM_PROJECT
TF_PROJECT_ID=zyanshu-dm-convert 
DM_PROJECT_ID=zyanshu-dm-convert-dm

# source ../../../../tools/alt-testing/create-projects.sh

gcloud auth application-default login

# Create DM resources
gcloud config set project $DM_PROJECT_ID
gcloud services enable deploymentmanager.googleapis.com
gcloud deployment-manager deployments create d1 --config kms.yaml

# Create Terraform resources
pushd alternatives/tf
gcloud config set project $TF_PROJECT_ID
terraform plan -var="deployment=d1" -var="project_id=${TF_PROJECT_ID}"
terraform apply -auto-approve -var="deployment=d1" -var="project_id=${TF_PROJECT_ID}"
popd

# Export DM and TF resources for comparison
gcloud kms keys list --keyring test--keyRing --location us-central1 --project $DM_PROJECT_ID | grep d1 | sed "s/${DM_PROJECT_ID}/PROJECT/" \
> /tmp/${DM_PROJECT_ID}.yaml

gcloud kms keys list --keyring test--keyRing --location us-central1 --project $TF_PROJECT_ID | grep d1 | sed "s/${TF_PROJECT_ID}/PROJECT/" \
> /tmp/${TF_PROJECT_ID}.yaml

# source ../../../../tools/alt-testing/delete-projects.sh

diff /tmp/${TF_PROJECT_ID}.yaml /tmp/${DM_PROJECT_ID}.yaml

if [[ $(diff /tmp/${TF_PROJECT_ID}.yaml /tmp/${DM_PROJECT_ID}.yaml) ]]; then
    echo "TF and DM outputs are NOT identical"
    exit 1
else
    echo "TF and DM outputs are identical"
fi

exit 0