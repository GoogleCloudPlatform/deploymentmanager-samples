set -e
# This script can sourced into test_alternatives script
# The following variables are expected to be defined in the parrent script
# TF_PROJECT_ID=
# KRM_PROJECT_ID=
# DM_PROJECT_ID=

# The following variables are local to this script and should be specified
BILLING_ACCOUNT=[BILLING_ACCOUNT]
FOLDER_ID=[FOLDER_ID]
CLUSTER_ID=[CLUSTER_ID]
ZONE=[ZONE]

# Create DM project
gcloud projects create $DM_PROJECT_ID --name="$DM_PROJECT_ID" --folder=$FOLDER_ID
gcloud alpha billing projects link $DM_PROJECT_ID --billing-account $BILLING_ACCOUNT
gcloud config set project $DM_PROJECT_ID

# Create TF project
gcloud projects create $TF_PROJECT_ID --name="$TF_PROJECT_ID" --folder=$FOLDER_ID
gcloud alpha billing projects link $TF_PROJECT_ID --billing-account $BILLING_ACCOUNT
gcloud config set project $TF_PROJECT_ID


# Create KCC project and configure KCC cluster
gcloud projects create $KRM_PROJECT_ID --name="$KRM_PROJECT_ID" --folder="$FOLDER_ID"
gcloud alpha billing projects link $KRM_PROJECT_ID --billing-account $BILLING_ACCOUNT
gcloud config set project $KRM_PROJECT_ID
gcloud services enable cloudresourcemanager.googleapis.com --project ${KRM_PROJECT_ID}
gcloud services enable container.googleapis.com --project ${KRM_PROJECT_ID}
gcloud container clusters create ${CLUSTER_ID} --workload-pool=${KRM_PROJECT_ID}.svc.id.goog --enable-ip-alias --zone $ZONE
gcloud container clusters get-credentials $CLUSTER_ID --zone=$ZONE
gcloud iam service-accounts create cnrm-system --project ${KRM_PROJECT_ID}
gcloud projects add-iam-policy-binding ${KRM_PROJECT_ID} --member "serviceAccount:cnrm-system@${KRM_PROJECT_ID}.iam.gserviceaccount.com" --role roles/owner
gcloud iam service-accounts add-iam-policy-binding \
    cnrm-system@${KRM_PROJECT_ID}.iam.gserviceaccount.com \
    --member="serviceAccount:${KRM_PROJECT_ID}.svc.id.goog[cnrm-system/cnrm-controller-manager]" \
    --role="roles/iam.workloadIdentityUser"
gsutil cp gs://cnrm/latest/release-bundle.tar.gz release-bundle.tar.gz
rm -rf release-bundle
tar zxvf release-bundle.tar.gz
sed -i.bak 's/${PROJECT_ID?}/'"$KRM_PROJECT_ID"'/' install-bundle-workload-identity/0-cnrm-system.yaml
kubectl apply -f install-bundle-workload-identity/
kubectl annotate namespace default "cnrm.cloud.google.com/project-id=${KRM_PROJECT_ID}" --overwrite