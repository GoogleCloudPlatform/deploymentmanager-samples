# IAM Custom Roles

Templated custom IAM role deployment

## Prerequisites

- Install [gcloud](https://cloud.google.com/sdk)
- Create a [GCP project, setup billing, enable requisite APIs](../project/README.md)


## Deployment

### Resources

- [Creating custom IAM roles](https://cloud.google.com/iam/docs/creating-custom-roles)
- [gcp-types/iam-v1:organizations.roles](https://cloud.google.com/iam/reference/rest/v1/organizations.roles/create)
- [gcp-types/iam-v1:projects.roles](https://cloud.google.com/iam/reference/rest/v1/projects.roles/create)


### Properties

See `properties` section in the schema files

-  [organization](organization_custom_role.py.schema)
-  [project](project_custom_role.py.schema)


### Deployment

#### Usage

1. Clone the [DM Samples_repository](https://github.com/GoogleCloudPlatform/deploymentmanager-sample)
2. Go to the [community/cloud-foundation](community/cloud-foundation) directory
3. Copy the example DM config to be used as a model for the deployment, in this case [examples/iam-custom-role.yaml](examples/iam-custom-role.yaml)
4. Change the values in the config file to match your specific GCP setup.
   Refer to the properties in the schema files described above.
5. Create your deployment as described below, replacing <YOUR_DEPLOYMENT_NAME>
   with your with your own deployment name


For example:

```
git clone https://github.com/GoogleCloudPlatform/deploymentmanager-sample
cd community/cloud-foundation
cp templates/iam_custom_role/examples/iam-custom-role.yaml my-iamcustomrole.yaml
vim my-iamcustomrole.yaml  # <== change values to match your GCP setup
gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config my-iamcustomrole.yaml
```

#### Create

```
gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config my-iamcustomrole.yaml
```


#### Delete

```
gcloud deployment-manager deployments delete <YOUR_DEPLOYMENT_NAME>
```


## Examples

- [iam-custom-role](examples/iam-custom-role.yaml)
