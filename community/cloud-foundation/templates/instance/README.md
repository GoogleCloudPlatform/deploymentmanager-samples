# Instance

Templated instance deployment

## Prerequisites

- Install [gcloud](https://cloud.google.com/sdk)
- Create a [GCP project, setup billing, enable requisite APIs](../project/README.md)

## Deployment

### Resources

- [compute.v1.instance](https://cloud.google.com/compute/docs/reference/rest/v1/instances)

### Properties

See `properties` section in the schema files

- [Instance](instance.py.schema)

### Outputs

See `outputs` section in the schema files

- [Instance](instance.py.schema)

### Deployment

#### Usage

1. Clone the [DM Samples_repository](https://github.com/GoogleCloudPlatform/deploymentmanager-samples)
2. Go to the [community/cloud-foundation](../../) directory
3. Copy the example DM config to be used as a model for the deployment, in this case [examples/instance.yaml](examples/instance.yaml)
4. Change the values in the config file to match your specific GCP setup.
   Refer to the properties in the schema files described above.
5. Create your deployment as described below, replacing <YOUR_DEPLOYMENT_NAME>
   with your with your own deployment name

For example:

``` bash
git clone https://github.com/GoogleCloudPlatform/deploymentmanager-samples
cd community/cloud-foundation
cp templates/instance/examples/instance.yaml my_instance.yaml
vim my_instance.yaml  # <== change values to match your GCP setup
gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config my_instance.yaml
```

#### Create

``` bash
gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config my_instance.yaml
```

#### Delete

``` bash
gcloud deployment-manager deployments delete <YOUR_DEPLOYMENT_NAME>
```

## Examples

- [Create Compute Instance with SSD drive and nginx installed](examples/instance.yaml)
