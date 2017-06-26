# Single VM with data disk

## Overview

This is a [Google Cloud Deployment
Manager](https://cloud.google.com/deployment-manager/overview) template which
deploys a single VM with a data disk. This is the most basic example of a
template, and takes only the VM zone as a parameter.

## Deploy the template

Use `vm.yaml` to deploy this example template. Before deploying, edit the file
and specify the zone in which to create the VM instance by replacing the
ZONE_TO_RUN.

When ready, deploy with the following command:

    gcloud deployment-manager deployments create single-vm --config vm.yaml
