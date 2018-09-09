# Logsink

This template creates a logsink (logging sink).

## Prerequisites

- Install [gcloud](https://cloud.google.com/sdk)
- Create a [GCP project, set up billing, enable requisite APIs](../project/README.md)
- Create one of the following:
    - [GCS bucket](https://cloud.google.com/storage/docs/json_api/v1/buckets)
    - [PubSub topic](https://cloud.google.com/pubsub/docs/reference/rest/v1/projects.topics)
    - [BigQuery dataset](https://cloud.google.com/bigquery/docs/reference/rest/v2/datasets)
- Grant the [logging.configWriter or logging.admin](https://cloud.google.com/logging/docs/access-control) IAM role to the project service account

## Deployment

### Resources

- [logging.v2.sink](https://cloud.google.com/logging/docs/reference/v2/rest/v2/projects.sinks)

### Properties

See `properties` section in the schema file(s):

-  [Logsink](logsink.py.schema)

### Usage

1. Clone the [Deployment Manager samples repository](https://github.com/GoogleCloudPlatform/deploymentmanager-samples):

```shell
    git clone https://github.com/GoogleCloudPlatform/deploymentmanager-samples
```

2. Go to the [community/cloud-foundation](../../) directory:

```shell
    cd community/cloud-foundation
```

3. Copy the example DM config to be used as a model for the deployment; in this case, [examples/logsink.yaml](examples/logsink.yaml):

```shell
    cp templates/logsink/examples/logsink.yaml my_logsink.yaml
```

4. Change the values in the config file to match your specific GCP setup (for properties, refer to the schema files listed above):

```shell
    vim my_logsink.yaml  # <== change values to match your GCP setup
```

5. Create your deployment (replace <YOUR_DEPLOYMENT_NAME> with the relevant deployment name):

```shell
    gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config my_logsink.yaml
```

6. In case you need to delete your deployment:

```shell
    gcloud deployment-manager deployments delete <YOUR_DEPLOYMENT_NAME>
```

## Examples

- [Logging entries exported to PubSub, Storage, and BigQuery](examples/logsink.yaml)
