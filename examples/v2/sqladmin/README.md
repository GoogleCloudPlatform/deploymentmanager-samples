# Cloud SQL Example

## Overview

This is a [Google Cloud Deployment
Manager](https://cloud.google.com/deployment-manager/overview) template that
deploys a Cloud SQL Master instance and N read-replicas. We also use a DM `action` to
add users to the instance and delete the root@% user. Actions are a currently undocumented feature for
calling arbitrary APIs.

> Note, CloudSQL does not allow parallel updates to the User table

## Prerequsites

You need to grant 

- [roles/cloudsql.admin](https://cloud.google.com/iam/docs/understanding-roles#sql_name_short_roles)  role
to the service account DM uses (```projectNumber@cloudservices.gserviceaccount.com```)

## Deploy the template

Use `sqladmin.yaml` to deploy this example template. When ready, deploy
with the following command:

```
gcloud deployment-manager deployments create my-database --config sqladmin.yaml
```

## More information

[Cloud SQL Documentation](https://cloud.google.com/sql/docs/)
