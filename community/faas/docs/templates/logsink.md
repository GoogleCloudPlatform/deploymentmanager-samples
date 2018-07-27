# Logsink

Templated logsink deployment

## Prerequisites

- Install [gcloud](https://cloud.google.com/sdk)
- Create a [GCP project, setup billing, enable requisite APIs](docs/templates/project.md)
- Create of the following:
    - [GCS bucket](https://cloud.google.com/storage/docs/json_api/v1/buckets)
    - [PubSub topic](https://cloud.google.com/pubsub/docs/reference/rest/v1/projects.topics)
    - [BigQuery dataset](https://cloud.google.com/bigquery/docs/reference/rest/v2/datasets)


## Deployment

### Resources

- [logging.v2.sink](https://cloud.google.com/logging/docs/reference/v2/rest/v2/projects.sinks)


### Properties

See `properties` section in the schema files

-  [logsink](../../templates/logsink.py.schema)


### Deployment

#### Usage

1. Clone the [DM Samples_repository](https://github.com/GoogleCloudPlatform/deploymentmanager-sample)
2. Go to the [community/faas](community/faas) directory
3. Copy the example DM config to be used as a model for the deployment, in this case [examples/logsink.yaml](examples/logsink.yaml)
4. Change the values in the config file to match your specific GCP setup.
   Refer to the properties in the schema files described above.
5. Create your deployment as described below, replacing <YOUR_DEPLOYMENT_NAME>
   with your with your own deployment name


For example:

```
git clone https://github.com/GoogleCloudPlatform/deploymentmanager-sample
cd community/faas
cp examples/logsink.yaml my-logsink.yaml
vim my-logsink.yaml  # <== change values to match your GCP setup
gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config my-logsink.yaml
```

#### Create

```
gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config logsink.yaml
```


#### Delete

```
gcloud deployment-manager deployments delete <YOUR_DEPLOYMENT_NAME>
```


## Examples

- [Log entries exported to PubSub, Storage, BigQuery](../examples/logsink.yaml)