set -e

TF_PROJECT_ID={TF_PROJECT_ID}
KRM_PROJECT_ID={KRM_PROJECT_ID}
DM_PROJECT_ID={DM_PROJECT_ID}


gcloud auth login

# Create DM resources
gcloud config set project $DM_PROJECT_ID
gcloud services enable deploymentmanager.googleapis.com
gcloud deployment-manager deployments create dm --config pubsub.yaml

# Create Terraform resources
gcloud config set project $TF_PROJECT_ID
gcloud config list --format 'value(core.project)'
terraform init
terraform apply -auto-approve -var="deployment=tf" -var="project_id=${TF_PROJECT_ID}"
# popd

#Create KCC resources
gcloud config set project $KRM_PROJECT_ID
gcloud container clusters get-credentials {CLUSTER_NAME} --zone us-central1-c
kubectl apply --namespace krm -f pubsub.yaml 


# Export DM and TF resources for comparison
gcloud pubsub subscriptions list --filter="labels.goog-dm:dm" --project {DM_PROJECT_ID} > dm.yaml

gcloud pubsub subscriptions list --filter=topic:my-pubsub-topic --project {TF_PROJECT_ID} --format=yaml > tf.yaml
gcloud pubsub subscriptions list --filter=topic:my-backup-topic --project {KRM_PROJECT_ID} --format=yaml >> krm.yaml


diff tf.yaml dm.yaml

if [[ $(diff dm.yaml tf.yaml) ]]; then
    echo "TF and DM outputs are NOT identical"
    exit 1
else
    echo "TF and DM outputs are identical"
fi

#diff /tmp/${KRM_PROJECT_ID}.yaml /tmp/${DM_PROJECT_ID}.yaml

#if [[ $(diff /tmp/${KRM_PROJECT_ID}.yaml /tmp/${DM_PROJECT_ID}.yaml) ]]; then
#    echo "KRM and DM outputs are NOT identical"
#    exit 1
#else
#    echo "KRM and DM outputs are identical"
#fi

exit 0
