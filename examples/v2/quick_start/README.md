# Quick start: Single VM deployment

## Overview

This is a [Google Cloud Deployment
Manager](https://cloud.google.com/deployment-manager/quickstart) configuration
file that deploys a single VM. It is the most basic example of a configuration
file. To use it, replace `[MY_PROJECT]` with your project ID, `[IMAGE_PROJECT]`
with a project name, like "debian-cloud", and `[FAMILY_NAME]`
with image family name, like "debian-9". Then run

    gcloud deployment-manager deployments create quick-start-deployment
    --config vm.yaml

For a quick introduction to Deployment Manager, see the [Quickstart
tutorial](https://cloud.google.com/deployment-manager/docs/quickstart).
