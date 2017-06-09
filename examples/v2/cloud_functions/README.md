# Cloud Functions Example

## Overview

This is a [Google Cloud Deployment
Manager](https://cloud.google.com/deployment-manager/overview) template that
deploys a Cloud Function, a PubSub topic, and calls the cloud function.

## Deploy the template

Use `cloud_function.yaml` to deploy this example template. If you would like to
use your own cloud function, you need to upload the content to your GCS bucket,
and change the sourceArchiveUrl parameter

When ready, deploy with the following command:

    gcloud deployment-manager deployments create my-function --config cloud_function.yaml

## More information

[Cloud Functions Documentation](https://cloud.google.com/functions/docs/)
