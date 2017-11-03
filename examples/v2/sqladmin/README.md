# Cloud SQL Example

## Overview

This is a [Google Cloud Deployment
Manager](https://cloud.google.com/deployment-manager/overview) template that
deploys a Cloud SQL instance and database. We also use a DM `action` to
delete the root user. Actions are a currently undocumented feature for
calling arbitrary APIs.

## Deploy the template

Use `sqladmin.yaml` to deploy this example template. When ready, deploy
with the following command:

    gcloud deployment-manager deployments create my-database --config sqladmin.yaml

## More information

[Cloud SQL Documentation](https://cloud.google.com/sql/docs/)
