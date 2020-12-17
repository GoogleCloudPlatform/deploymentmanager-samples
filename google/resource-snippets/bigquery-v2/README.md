# Bigquery Snippets

## DM

```bash
gcloud services enable deploymentmanager.googleapis.com
gcloud deployment-manager deployments create d1 --config bigquery.yaml
```

## Terraform

```bash
TF_PROJECT_ID=[TF_PROJECT_ID]
gcloud config set project $TF_PROJECT_ID
cd alternatives/tf
terraform plan -var="deployment=d1" -var="project_id=${TF_PROJECT_ID}"
terraform apply -auto-approve -var="deployment=d1" -var="project_id=${TF_PROJECT_ID}"
```

## KRM

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
