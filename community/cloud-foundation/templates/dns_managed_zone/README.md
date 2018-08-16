# Cloud DNS Managed Zone

Cloud DNS managed zone

## Prerequisites

- Install [gcloud](https://cloud.google.com/sdk)
- Create a [GCP project, setup billing, enable requisite APIs](../project/README.md)

## Deployment

### Resources

- [dns.v1.managedZone'](https://cloud.google.com/dns/docs/)

### Properties

See `properties` section in the schema files

-  [Cloud DNS Managed Zone](dns_managed_zone.py.schema)


### Deployment

#### Usage

1. Clone the [DM Samples_repository](https://github.com/GoogleCloudPlatform/deploymentmanager-sample)
2. Go to the [community/cloud-foundation](community/cloud-foundation) directory
3. Copy the example DM config to be used as a model for the deployment, in this case [examples/dns_managed_zone.yaml](examples/dns_managed_zone.yaml)
4. Change the values in the config file to match your specific GCP setup.
   Refer to the properties in the schema files described above.
5. Create your deployment as described below, replacing <YOUR_DEPLOYMENT_NAME>
   with your with your own deployment name


For example:

```
git clone https://github.com/GoogleCloudPlatform/deploymentmanager-sample
cd community/cloud-foundation
cp templates/dns_managed_zone/examples/dns_managed_zone.yaml my_dns_managed_zone.yaml
vim my_dns_managed_zone.yaml  # <== change values to match your GCP setup
gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config my_dns_managed_zone.yaml
```

#### Create

```
gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config my_dns_managed_zone.yaml
```


#### Delete

```
gcloud deployment-manager deployments delete <YOUR_DEPLOYMENT_NAME>
```


## Examples

- [Cloud DNS Managed Zone](examples/dns_managed_zone.yaml)

