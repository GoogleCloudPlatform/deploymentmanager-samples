# Pubsub

Templated Pub/Sub deployment

## Prerequisites

- Install [gcloud](https://cloud.google.com/sdk)
- Create a [GCP project, setup billing, enable requisite APIs](../project/README.md)

## Deployment

### Resources

- [pubsub.v1.topic](https://cloud.google.com/pubsub/docs/reference/rest/v1/projects.topics)
- [pubsub.v1.subscription](https://cloud.google.com/pubsub/docs/reference/rest/v1/projects.subscriptions)

### Properties

See `properties` section in the schema file

- [Pub/Sub](pubsub.py.schema)

### Outputs

See `outputs` section in the schema file

- [Pub/Sub](pubsub.py.schema)

### Deployment

#### Usage

1. Clone the [DM Samples_repository](https://github.com/GoogleCloudPlatform/deploymentmanager-samples)
2. Go to the [community/cloud_foundation](../../) directory
3. Copy the example DM config to be used as a model for the deployment, in this case [examples/pubsub.yaml](examples/pubsub.yaml)
4. Change the values in the config file to match your specific GCP setup.
   Refer to the properties in the schema files described above.
5. Create your deployment as described below, replacing <YOUR_DEPLOYMENT_NAME>
   with your with your own deployment name

For example:

``` bash
git clone https://github.com/GoogleCloudPlatform/deploymentmanager-samples
cd community/cloud-foundation
cp templates/pubsub/examples/pubsub.yaml my_pubsub.yaml
vim my_pubsub.yaml  # <== change values to match your GCP setup
gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config my_pubsub.yaml
```

#### Create

``` bash
gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config my_pubsub.yaml
```

#### Delete

``` bash
gcloud deployment-manager deployments delete <YOUR_DEPLOYMENT_NAME>
```

## Examples

- [Create Pub/Sub topic with two subscriptions and IAM policies set](examples/pubsub.yaml)
