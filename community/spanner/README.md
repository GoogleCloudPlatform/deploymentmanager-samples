# Cloud Spanner

## Overview

This is a [Google Cloud Deployment
Manager](https://cloud.google.com/deployment-manager/overview) template which
deploys a Cloud Spanner instance.

## Deploy the template

Use `config.yaml` to deploy this example template.
You can set the instance configuration using the instanceConfig property in the config.yaml.
The list of available `instanceConfig` values can be found using:

    gcloud spanner instance-configs list

When ready, deploy with the following command:

    gcloud deployment-manager deployments create YOUR_DEPLOYMENT_NAME --config config.yaml

See more documentation at [Cloud Spanner](https://cloud.google.com/spanner)
