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

## Regarding the function source

Our samples reference the function source (in the `function` directory) as
`gs://cloud-function-sample/function.zip`. Cloud Functions doesn't have a
way to inline the function code, so any function you write needs to be uploaded
to a GCS bucket or use Cloud Source Repositories: instructions can be found
[here](https://cloud.google.com/functions/docs/deploying/filesystem) and
[here](https://cloud.google.com/functions/docs/deploying/repo). Deployment
Manager can't create zip files, so some these steps have to be done outside
of your deployment.

## More information

[Cloud Functions Documentation](https://cloud.google.com/functions/docs/)
