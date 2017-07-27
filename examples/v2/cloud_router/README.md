# Cloud Router Example

## Overview

This is a [Google Cloud Deployment
Manager](https://cloud.google.com/deployment-manager/overview) template that
deploys a Cloud Router and VPN Tunnel.

## Deploy the template

Use `cloud_router.yaml` to deploy this example template after changing
YOUR_DEPLOYMENT_NAME and REGION_TO_RUN.

When ready, deploy with the following command:

    gcloud deployment-manager deployments create my-router --config cloud_router.yaml

## More information

[Cloud Router Documentation](https://cloud.google.com/compute/docs/cloudrouter)
