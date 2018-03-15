# Custom IAM Role

## Overview

This is a [Google Cloud Deployment
Manager](https://cloud.google.com/deployment-manager/overview) template which
deploys a custom role.

Be aware that to successfully use these templates, you may need to grant
additional roles to the default Google APIs service account. See [Best
Practices](https://cloud.google.com/deployment-manager/docs/best-practices/#permissions)
for more information.

## Deploy the template

When ready, deploy a project custom role with the following command:

    gcloud deployment-manager deployments create YOUR_DEPLOYMENT_NAME --config project_custom_role.yaml

or deploy an organization custom role with the following command:

    gcloud deployment-manager deployments create YOUR_DEPLOYMENT_NAME --config organization_custom_role.yaml

When using `organization_custom_role.yaml`, the organizationId field needs to
be populated with the organization id where the custom role will be created under.

See more documentation at [IAM Roles](https://cloud.google.com/iam/reference/rest/v1/projects.roles/create)
