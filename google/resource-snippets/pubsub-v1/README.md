# PubSub Snippets

## DM

Setup:

* Install [gcloud](https://cloud.google.com/sdk/docs/install)
* Create GCP project

```bash
DM_PROJECT_ID=[DM_PROJECT_ID]
gcloud config set project $DM_PROJECT_ID
gcloud services enable pubsub.googleapis.com
gcloud services enable deploymentmanager.googleapis.com
gcloud deployment-manager deployments create deployment --config pubsub.yaml
```

## Terraform

Setup:

* Install [gcloud](https://cloud.google.com/sdk/docs/install)
* Install [terraform](https://www.terraform.io/downloads.html)
* Create GCP project
* Setup [Credential](https://registry.terraform.io/providers/hashicorp/google/latest/docs/guides/getting_started#adding-credentials)

```bash
TF_PROJECT_ID=[TF_PROJECT_ID]
gcloud config set project $TF_PROJECT_ID
gcloud services enable pubsub.googleapis.com
cd alternatives/tf
terraform init
terraform apply -auto-approve -var="deployment=deployment" -var="project_id=${TF_PROJECT_ID}"
```
## KRM

Setup:

* Install [gcloud](https://cloud.google.com/sdk/docs/install)
* Install [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
* Install [kpt](https://github.com/GoogleContainerTools/kpt#installation)
* Create GCP project

## Testing

```bash
sh test_alternatives.sh
```
