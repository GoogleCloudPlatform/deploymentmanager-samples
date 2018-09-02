# DNS Resource RecordSets

This Template manages Cloud DNS records via record-sets

## Prerequisites

- Install [gcloud](https://cloud.google.com/sdk)
- Create a [GCP project, setup billing, enable requisite APIs](../project/README.md)
- Grant [dns.admin](https://cloud.google.com/dns/access-control) role to the Deployment Manager `serviceAccount` 

## Deployment

### Resources

- [gcp-types/dns-v1](https://cloud.google.com/dns/api/v1/changes)

### Properties

See `properties` section in the schema files

- [DNS Records](dns_records.py.schema)

### Usage

1. Clone the [DM Samples_repository](https://github.com/GoogleCloudPlatform/deploymentmanager-samples):

```bash
    git clone https://github.com/GoogleCloudPlatform/deploymentmanager-samples
```

2. Go to the [community/cloud-foundation](../../) directory:

```bash
    cd community/cloud-foundation
```

3. Copy the example DM config to be used as a model for the deployment; in this case, [examples/dns_records.yaml](examples/dns_records.yaml):

```bash
    cp templates/dns_records/examples/dns_records.yaml my_dns_records.yaml
```

4. Change the values in the config file to match your specific GCP setup (for properties, refer to the schema files listed above):

```bash
    vim my_cloud_router.yaml  # <== change values to match your GCP setup
```

5. Create your deployment (replace <YOUR_DEPLOYMENT_NAME> with the relevant deployment name):

```bash
    gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config my_cloud_router.yaml
```

6. In case you need to delete your deployment:

```bash
    gcloud deployment-manager deployments delete <YOUR_DEPLOYMENT_NAME>
```

## Examples

- [Create DNS ResourceRecordSets](examples/dns_records.yaml)

