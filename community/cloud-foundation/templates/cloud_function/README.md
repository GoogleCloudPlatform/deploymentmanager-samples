# Cloud Function

This template creates a Cloud Function.

## Prerequisites

- Install [gcloud](https://cloud.google.com/sdk)
- Create a [GCP project, set up billing, enable requisite APIs](../project/README.md)
- Enable [Cloud Build API](https://cloud.google.com/cloud-build/docs/api/reference/rest/)
- Enable [Cloud Functions API](https://cloud.google.com/functions/docs/reference/rest/)
- In order to create a deployment, make sure your account has project editor level access
or have been granted [roles/deploymentmanager.editor](https://cloud.google.com/deployment-manager/docs/access-control#predefined_roles) role
- In order for DM to create a cloud function, make sure that [Google APIs service account](https://cloud.google.com/deployment-manager/docs/access-control#access_control_for_deployment_manager)
has **default** permissions, or was explicitly granted [roles/cloudfunctions.developer](https://cloud.google.com/functions/docs/reference/iam/roles#standard-roles) role
- In order for cloud function to subscribe to PubSub topics or listen to Storage events, make sure that [Cloud Functions service account](https://cloud.google.com/functions/docs/concepts/iam#cloud_functions_service_account)
has **default** permissions or has been granted [CloudFunctions.ServiceAgent](https://cloud.google.com/functions/docs/concepts/iam#cloud_functions_service_account) role

## Deployment

### Resources

- [cloudfunctions.v1beta2.function](https://cloud.google.com/functions/docs/reference/rest/v1beta2/projects.locations.functions)
- [storage.v1.bucket](https://cloud.google.com/storage/docs/json_api/v1/buckets)

### Properties

See the `properties` section in the schema file(s):
- [Cloud Function](cloud_function.py.schema)

### Usage

1. Clone the [DM Samples_repository](https://github.com/GoogleCloudPlatform/deploymentmanager-samples):

```
    git clone https://github.com/GoogleCloudPlatform/deploymentmanager-samples
```

2. Go to the [community/cloud-foundation](../../) directory:

```
    cd community/cloud-foundation
```

3. Copy the example DM config to be used as a model for the deployment; in this case, [examples/cloud_function.yaml](examples/cloud_function.yaml):

```
    cp templates/cloud_function/examples/cloud_function.yaml my_cloud_function.yaml
```

4. Change the values in the config file to match your specific GCP setup (for properties, refer to the schema files listed above):

```
    vim my_cloud_function.yaml  # <== change values to match your GCP setup
```

5. Create your deployment (replace <YOUR_DEPLOYMENT_NAME> with the relevant deployment name):

```
    gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config my_cloud_function.yaml
```

**Please note**, that Cloud Function HTTP trigger doesn't have authentication
built in. In other words any user having the link to HTTP trigger will be able
to call it.


6. In case you need to delete your deployment:

```
    gcloud deployment-manager deployments delete <YOUR_DEPLOYMENT_NAME>
```

**Please note**, that for cloud functions created from local source code,
deleting a deployment won't delete a bucket, where the function source code was
uploaded to during the build. It also won't clean up a [Cloud Build](https://cloud.google.com/cloud-build/)
history.


## Examples

- [Create HTTPS triggered JavaScript Cloud Function from local source code](examples/cloud_function.yaml)
