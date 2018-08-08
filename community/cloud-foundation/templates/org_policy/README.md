# Org Policy

Templated Organization Policies

## Prerequisites

- Install [gcloud](https://cloud.google.com/sdk)
- Create a [GCP project, setup billing, enable requisite APIs](../project/README.md)


## Deployment

### Resources

- [cloudresourcemanager.v1.project](https://cloud.google.com/resource-manager/reference/rest/v1/projects/setOrgPolicy)


### Properties

See `properties` section in the schema files

-  [Org Policy](org_policy.py.schema)


### Deployment

#### Usage

1. Clone the [DM Samples_repository](https://github.com/GoogleCloudPlatform/deploymentmanager-sample)
2. Go to the [community/cloud-foundation](community/cloud-foundation) directory
3. Copy the example DM config to be used as a model for the deployment, in this case [examples/org_policy.yaml](examples/org_policy.yaml)
4. Change the values in the config file to match your specific GCP setup.
   Refer to the properties in the schema files described above.
5. Create your deployment as described below, replacing <YOUR_DEPLOYMENT_NAME>
   with your with your own deployment name


For example:

```
git clone https://github.com/GoogleCloudPlatform/deploymentmanager-sample
cd community/cloud-foundation
cp templates/org_policy/exampples/org_policy.yaml my_org_policy.yaml
vim my_org_policy.yaml  # <== change values to match your GCP setup
gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config my_org_policy.yaml
```

#### Create

```
gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config my_org_policy.yaml
```


#### Delete

```
gcloud deployment-manager deployments delete <YOUR_DEPLOYMENT_NAME>
```


## Examples

- [Org Policy](examples/org_policy.yaml)
