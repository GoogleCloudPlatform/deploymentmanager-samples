# Custom IAM Role

## Overview

This is a [Google Cloud Deployment
Manager](https://cloud.google.com/deployment-manager/overview) template which
deploys a custom role.

## Deploy the template

Use `custom_role.yaml` to deploy this example template.

When ready, deploy with the following command:

    gcloud deployment-manager deployments create YOUR_DEPLOYMENT_NAME --config custom_role.yaml

See more documentation at [IAM Roles](https://cloud.google.com/iam/reference/rest/v1/projects.roles/create)