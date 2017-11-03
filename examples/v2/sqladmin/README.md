# Cloud SQL Example

## Overview

This is a [Google Cloud Deployment
Manager](https://cloud.google.com/deployment-manager/overview) template that
deploys a Cloud SQL instance and database.

## Deploy the template

Use `sqladmin.yaml` to deploy this example template. When ready, deploy
with the following command:

    gcloud deployment-manager deployments create my-database --config sqladmin.yaml

## Deleting the root user

If you want to delete the root user, you can add the following resource.

    - name: delete-root
      action: gcp-types/sqladmin-v1beta4:sql.users.delete
      metadata:
        runtimePolicy:
        - CREATE
      properties:
        project: PROJECT_NAME
        instance: YOUR_INSTANCE_NAME
        host: localhost
        name: root

This resource uses an `action`. These are currently an undocumented feature of
Deployment Manager useful for calling arbitrary APIs.

## More information

[Cloud SQL Documentation](https://cloud.google.com/sql/docs/)
