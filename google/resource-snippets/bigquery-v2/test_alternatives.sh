set -e

# assumes that the following projects are created and kubectl context is set to a cluster in KRM_PROJECT
TF_PROJECT_ID=[TF_PROJECT_ID]
KRM_PROJECT_ID=[KRM_PROJECT_ID]
DM_PROJECT_ID=[DM_PROJECT_ID]

# source ../../../../tools/alt-testing/create-projects.sh

gcloud auth application-default login

# Create DM resources
gcloud config set project $DM_PROJECT_ID
gcloud services enable deploymentmanager.googleapis.com
gcloud deployment-manager deployments create d1 --config bigquery.yaml

# Create Terraform resources
pushd alternatives/tf
gcloud config set project $TF_PROJECT_ID
terraform plan -var="deployment=d1" -var="project_id=${TF_PROJECT_ID}"
terraform apply -auto-approve -var="deployment=d1" -var="project_id=${TF_PROJECT_ID}"
popd

# Create KCC resources
cp -R alternatives/krm /tmp/krm_${KRM_PROJECT_ID}
pushd /tmp/krm_${KRM_PROJECT_ID}
kpt cfg set . deployment d1
kubectl apply -f bigquery.yaml
kubectl  wait --for=condition=Ready BigQueryTable --all
popd
rm -rf krm_${KRM_PROJECT_ID}


# Export DM and TF resources for comparison
{ gcloud alpha bq datasets list --project=${DM_PROJECT_ID} --format=yaml && gcloud alpha bq tables list --dataset=d1dataset --project=${DM_PROJECT_ID} --format=yaml; } \
    | sed "s/${DM_PROJECT_ID}/PROJECT/" | sed "s/creationTime: .*/creationTime: TIME/" \
    > /tmp/${DM_PROJECT_ID}.yaml

{ gcloud alpha bq datasets list --project=${TF_PROJECT_ID} --format=yaml && gcloud alpha bq tables list --dataset=d1dataset --project=${TF_PROJECT_ID} --format=yaml; } \
    | sed "s/${TF_PROJECT_ID}/PROJECT/" | sed "s/creationTime: .*/creationTime: TIME/" \
    > /tmp/${TF_PROJECT_ID}.yaml

{ gcloud alpha bq datasets list --project=${KRM_PROJECT_ID} --format=yaml && gcloud alpha bq tables list --dataset=d1dataset --project=${KRM_PROJECT_ID} --format=yaml; } \
    | sed "s/${KRM_PROJECT_ID}/PROJECT/" | sed "s/creationTime: .*/creationTime: TIME/" | sed "/cnrm-lease-.*/d" | sed "/managed-by-cnrm.*/d" \
    > /tmp/${KRM_PROJECT_ID}.yaml

# source ../../../../tools/alt-testing/delete-projects.sh

diff /tmp/${TF_PROJECT_ID}.yaml /tmp/${DM_PROJECT_ID}.yaml

if [[ $(diff /tmp/${TF_PROJECT_ID}.yaml /tmp/${DM_PROJECT_ID}.yaml) ]]; then
    echo "TF and DM outputs are NOT identical"
    exit 1
else
    echo "TF and DM outputs are identical"
fi

diff /tmp/${KRM_PROJECT_ID}.yaml /tmp/${DM_PROJECT_ID}.yaml

if [[ $(diff /tmp/${KRM_PROJECT_ID}.yaml /tmp/${DM_PROJECT_ID}.yaml) ]]; then
    echo "KRM and DM outputs are NOT identical"
    exit 1
else
    echo "KRM and DM outputs are identical"
fi

exit 0