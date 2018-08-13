# Folder

Templated Folder deployment

## Prerequisites
- Install [gcloud](https://cloud.google.com/sdk)
- Create a [GCP project, setup billing, enable requisite APIs](../project/README.md)


## Deployment

### Resources

- [gcp-types/cloudresourcemanager-v2:folders](https://cloud.google.com/resource-manager/reference/rest/v2/folders/create)


### Properties

See `properties` section in the schema files

-  [Folder](folder.py.schema)


### Deployment

#### Usage

1. Clone the [DM Samples_repository](https://github.com/GoogleCloudPlatform/deploymentmanager-samples)
2. Go to the [community/cloud-foundation](../../../cloud-foundation) directory
3. Copy the example DM config to be used as a model for the deployment, in this case [examples/folder.yaml](examples/folder.yaml)
4. Change the values in the config file to match your specific GCP setup.
   Refer to the properties in the schema files described above.
5. Create your deployment as described below, replacing <YOUR_DEPLOYMENT_NAME>
   with your with your own deployment name


For example:

```
git clone https://github.com/GoogleCloudPlatform/deploymentmanager-samples
cd community/cloud-foundation
cp templates/folder/examples/folder.yaml my_folder.yaml
vim my_folder.yaml  # <== change values to match your GCP setup
gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config my_folder.yaml
```

#### Create

```
gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config my_folder.yaml
```


#### Delete

```
gcloud deployment-manager deployments delete <YOUR_DEPLOYMENT_NAME>
```


## Examples

- [Creating a folder under an organization and a folder](examples/folder.yaml)
