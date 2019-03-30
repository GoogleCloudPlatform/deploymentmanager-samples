# Creating Folders Through Deployment Manager

## Overview

This is a
[Google Cloud Deployment Manager](https://cloud.google.com/deployment-manager/overview)
template that creates a folder using the Cloud Resource Manager API.

## Prerequisites

1.  Give the DM Service Account the following permissions to manager a folder:

    *   'roles/resourcemanager.folderCreator' and
        'roles/resourcemanager.folderEditor' (for deletion permission)
        *   Visible in Cloud Console's IAM permissions in Resource Manager ->
            Folder [Creator|Editor].

## Deploying the templates.

Use `folder.yaml` to deploy this example template.

1.  Customize the yaml config for your context. You will need to:

    *   Set the name of the resource, which will be the display name of the
        folder.
    *   Set the name of the
        [parent resource](https://cloud.google.com/resource-manager/reference/rest/v2/folders/create),
        such as another folder.

When ready, deploy with the following command:

    gcloud deployment-manager deployments create my-folder --config folder.yaml
