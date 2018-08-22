# BigQuery

Templated BigQuery deployment

## Prerequisites
- Install [gcloud](https://cloud.google.com/sdk)
- Create a [GCP project, setup billing, enable requisite APIs](../project/README.md)
- Grant [roles/bigquery.dataEditor or roles/bigquery.admin](https://cloud.google.com/bigquery/docs/access-control)


## Deployment

### Resources

- [bigquery.v2.dataset](https://cloud.google.com/bigquery/docs/reference/rest/v2/datasets)
- [bigquery.v2.tables](https://cloud.google.com/bigquery/docs/reference/rest/v2/tables)


### Properties

See `properties` section in the schema files

- [BigQuery Dataset](bigquery_dataset.py.schema)
- [BigQuery Tables](bigquery_table.py.schema)


### Deployment

#### Usage

1. Clone the [DM Samples_repository](https://github.com/GoogleCloudPlatform/deploymentmanager-sample)
2. Go to the [community/cloud-foundation](../../) directory
3. Copy the example DM config to be used as a model for the deployment, in this case [examples/bigquery.yaml](examples/bigquery.yaml)
4. Change the values in the config file to match your specific GCP setup.
   Refer to the properties in the schema files described above.
5. Create your deployment as described below, replacing <YOUR_DEPLOYMENT_NAME>
   with your with your own deployment name


For example:

```
git clone https://github.com/GoogleCloudPlatform/deploymentmanager-sample
cd community/cloud-foundation
cp templates/bigquery/examples/bigquery.yaml my_bigquery.yaml
vim my_bigquery.yaml  # <== change values to match your GCP setup
gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config my_bigquery.yaml
```

#### Create

```
gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config my_bigquery.yaml
```


#### Delete

```
gcloud deployment-manager deployments delete <YOUR_DEPLOYMENT_NAME>
```


## Examples

- [Bigquery Dataset and Table](examples/bigquery.yaml)
