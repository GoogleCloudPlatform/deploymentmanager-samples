# Cloud Functions Example

## Overview

This is a
[Google Cloud Deployment Manager](https://cloud.google.com/deployment-manager/overview)
template that deploys a Cloud Function and calls the cloud function.

## NOTE
As of November 1, 2019, newly created Functions are private-by-default and will require [appropriate IAM permissions](https://cloud.google.com/functions/docs/reference/iam/roles) to be invoked. See the [cloud foundation toolkit](https://github.com/GoogleCloudPlatform/cloud-foundation-toolkit/tree/master/dm/templates/cloud_function) project for example implementations.

## Deploy the template

Use `cloud_function.yaml` to deploy this example template. This template uses
Container Builder to push the file contents into GCS so make sure you grant
access to your Container Builder service account which is
<projectNumber>@cloudbuild.gserviceaccount.com to be able to write to your
bucket

When ready, deploy with the following command:

```shell
gcloud deployment-manager deployments create my-function --config cloud_function.yaml
```

## Regarding the function source

Also it is possible to use Cloud Source Repositories: instructions can be found
[here](https://cloud.google.com/functions/docs/deploying/filesystem) and
[here](https://cloud.google.com/functions/docs/deploying/repo).

## More information

[Cloud Functions Documentation](https://cloud.google.com/functions/docs/)
