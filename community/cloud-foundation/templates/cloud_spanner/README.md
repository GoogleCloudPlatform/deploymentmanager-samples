# Cloud Spanner

Templated Cloud Spanner Deployment

## Prerequisites
- Install [gcloud](https://cloud.google.com/sdk)
- Create a [GCP project, set up billing, enable requisite APIs](../project/README.md)
- Assign the [spanner.admin](https://cloud.google.com/spanner/docs/iam) role to the project service account in order to have setIamPolicy permission.


## Deployment

### Resources

- [gcp-types/spanner-v1](https://cloud.google.com/spanner/docs/reference/rest/v1/projects.instances)


### Properties

See the `properties` section in the schema file(s):
-  [Cloud Spanner](cloud_spanner.py.schema)


#### Usage

1. Clone the [DM Samples_repository](https://github.com/GoogleCloudPlatform/deploymentmanager-samples)
```
    git clone https://github.com/GoogleCloudPlatform/deploymentmanager-samples
```

2. Go to the [community/cloud-foundation](../../../cloud-foundation) directory
```
    cd community/cloud-foundation
```

3. Copy the example DM config to be used as a model for the deployment, in this case [examples/cloud_spanner.yaml](examples/cloud_spanner.yaml)
```
    cp templates/cloud_spanner/examples/cloud_spanner.yaml my_cloud_spanner.yaml
```

4. Change the values in the config file to match your specific GCP setup.
   Refer to the properties in the schema files described above.
```
    vim my_cloud_spanner.yaml  # <== change values to match your GCP setup
```


5. Create your deployment as described below, replacing <YOUR_DEPLOYMENT_NAME>
   with your with your own deployment name

```
    gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config my_cloud_spanner.yaml
```

6. In case you need to delete your deployment: 
```
gcloud deployment-manager deployments delete <YOUR_DEPLOYMENT_NAME>
```


## Examples

- [Creating a cloud spanner instance cluster, database and set permissions](examples/cloud_spanner.yaml)
