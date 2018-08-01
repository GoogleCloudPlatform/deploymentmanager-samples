# VPN

Templated VPN deployment

## Prerequisites

- Install [gcloud](https://cloud.google.com/sdk)
- Create a [GCP project, setup billing, enable requisite APIs](docs/templates/project.md)
- Create a [network](docs/templates/network.md)

## Deployment

### Resources

- [compute.v1.targetVpnGateway](https://cloud.google.com/compute/docs/reference/latest/targetVpnGateways)
- [compute.v1.address](https://cloud.google.com/compute/docs/reference/rest/v1/addresses)
- [compute.v1.forwardingRule](https://cloud.google.com/compute/docs/reference/latest/forwardingRule)
- [compute.v1.vpnTunnel](https://cloud.google.com/compute/docs/reference/latest/vpnTunnel)
- [gcp-types/compute-v1:compute.routers.patch](https://www.googleapis.com/discovery/v1/apis/compute/v1/rest)


### Properties

See `properties` section in the schema files

-  [VPN](../../templates/vpn.py.schema)


### Deployment

#### Usage

1. Clone the [DM Samples_repository](https://github.com/GoogleCloudPlatform/deploymentmanager-sample)
2. Go to the [community/faas](community/faas) directory
3. Copy the example DM config to be used as a model for the deployment, in this case [examples/vpn.yaml](examples/vpn.yaml)
4. Change the values in the config file to match your specific GCP setup.
   Refer to the properties in the schema files described above.
5. Create your deployment as described below, replacing <YOUR_DEPLOYMENT_NAME>
   with your with your own deployment name


For example:

```
git clone https://github.com/GoogleCloudPlatform/deploymentmanager-sample
cd community/faas
cp examples/vpn.yaml my-vpn.yaml
vim my-vpn.yaml  # <== change values to match your GCP setup
gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config my-vpn.yaml
```

#### Create

```
gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config my-vpn.yaml
```


#### Delete

```
gcloud deployment-manager deployments delete <YOUR_DEPLOYMENT_NAME>
```


## Examples

- [VPN](../examples/vpn.yaml)
