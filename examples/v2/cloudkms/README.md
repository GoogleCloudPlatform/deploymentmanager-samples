# Cloud KMS

## Overview

This is a [Google Cloud Deployment
Manager](https://cloud.google.com/deployment-manager/overview) template which
deploys a Cloud KMS Key.

## Deploy the template

Use `config.yaml` to deploy this example template.

When ready, deploy with the following command:

    gcloud deployment-manager deployments create YOUR_DEPLOYMENT_NAME --config config.yaml

Cloud KMS KeyRings and CryptoKeys cannot be deleted, so you need to abandon the resources.
    
    gcloud deployment-manager deployments delete YOUR_DEPLOYMENT_NAME --delete-policy=ABANDON

See more documentation at [Cloud KMS](https://cloud.google.com/kms)
