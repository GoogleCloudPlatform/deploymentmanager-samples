# Cloud Container Builder Example

## Overview

This is a [Google Cloud Deployment
Manager](https://cloud.google.com/deployment-manager/overview) template that
creates a Cloud Container Builder build.

This sample uses the undocumented DM Actions feature (estimated to come out
in Q2 2018) to call the Cloud Container Builder projects.builds.create API.
This doesn't create a DM resource like you would normally see, it just calls
the API as specified in the metadata.runtimePolicy section. This section may
contain the values UPDATE\_ALWAYS (call the API for create or update changes
in the deployment), CREATE (only call on create), UPDATE\_ON\_CHANGE (call
when the action changes), DELETE (call on deletes).


## Deploy the template

Use `cloudbuild.yaml` to deploy this example template. Enable the API
[here]( https://pantheon.corp.google.com/apis/library/cloudbuild.googleapis.com/).
You also need to ensure the Cloud Container Builder service account has read
access to DM for the sample (Project Viewer is the simplest option).  More
information can be found
[here](https://cloud.google.com/container-builder/docs/how-to/service-account-permissions).

When ready, deploy with the following command:

    gcloud deployment-manager deployments create my-build --config cloudbuild.yaml

## More information

[Cloud Container Builder documentation](https://cloud.google.com/container-builder/docs/)
