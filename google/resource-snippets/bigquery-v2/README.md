# Bigquery Snippets

## DM

Setup:

* Install [gcloud](https://cloud.google.com/sdk/docs/install)
* Create GCP project

```bash
DM_PROJECT_ID=[DM_PROJECT_ID]
gcloud config set project $DM_PROJECT_ID
gcloud services enable deploymentmanager.googleapis.com
gcloud deployment-manager deployments create d1 --config bigquery.yaml
```

## Terraform

Setup:

* Install [gcloud](https://cloud.google.com/sdk/docs/install)
* Install [terraform](https://www.terraform.io/downloads.html)
* Create GCP project

```bash
TF_PROJECT_ID=[TF_PROJECT_ID]
gcloud config set project $TF_PROJECT_ID
cd alternatives/tf
terraform init
terraform plan -var="deployment=d1" -var="project_id=${TF_PROJECT_ID}"
terraform apply -auto-approve -var="deployment=d1" -var="project_id=${TF_PROJECT_ID}"
```

## KRM

Setup:

* Install [gcloud](https://cloud.google.com/sdk/docs/install)
* Install [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
* Install [kpt](https://github.com/GoogleContainerTools/kpt#installation)
* Create GCP project

```bash
gcloud container clusters get-credentials [CLUSTER_ID] --zone=[ZONE]
cd alternatives/krm
kpt cfg set . deployment d1
kubectl apply -f bigquery.yaml
```

## Testing

```bash
sh test_alternatives.sh
```
