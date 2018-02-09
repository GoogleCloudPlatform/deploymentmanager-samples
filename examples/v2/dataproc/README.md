# Dataproc Example

## Overview

This is a [Google Cloud Deployment
Manager](https://cloud.google.com/deployment-manager/overview) template that
deploys a dataproc cluster.

## Deploy the template

Use `dataproc.yaml` to deploy this example template after changing
REGION_TO_RUN and ZONE_TO_RUN.

When ready, deploy with following command:

    gcloud deployment-manager deployments create DEPLOYMENT_NAME --config dataproc.yaml

## More information

[Dataproc Documentation](https://cloud.google.com/dataproc/)
