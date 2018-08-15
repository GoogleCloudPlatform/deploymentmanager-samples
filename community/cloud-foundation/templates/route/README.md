# Routes

Templated route deployment

## Prerequisites

- Install [gcloud](https://cloud.google.com/sdk)
- Create a [GCP project, setup billing, enable requisite APIs](../project/README.md)
- Create a [network](../network/README.md)
- Depending on the traffic destination specified, you may need to create one or more of the following:
  - [VM](../vm/vm.md)
  - [VPN Tunnel](../vpn/README.md)


## Deployment

### Resources

- [compute.v1.route](https://cloud.google.com/compute/docs/reference/rest/v1/routes)


### Properties

See `properties` section in the schema files

-  [Route](route.py.schema)

### Deployment

#### Usage

1. Clone the [DM Samples_repository](https://github.com/GoogleCloudPlatform/deploymentmanager-sample)
2. Go to the [community/cloud-foundation](community/cloud-foundation) directory
3. Copy the example DM config to be used as a model for the deployment, in this case [examples/route.yaml](examples/route.yaml)
4. Change the values in the config file to match your specific GCP setup.
   Refer to the properties in the schema files described above.
5. Create your deployment as described below, replacing <YOUR_DEPLOYMENT_NAME>
   with your with your own deployment name


For example:

```
git clone https://github.com/GoogleCloudPlatform/deploymentmanager-sample
cd community/cloud-foundation
cp templates/route/examples/route.yaml my_route.yaml
vim my_route.yaml  # <== change values to match your GCP setup
gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config my_route.yaml
```

#### Create

```
gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config my_route.yaml
```


#### Delete

```
gcloud deployment-manager deployments delete <YOUR_DEPLOYMENT_NAME>
```


## Examples

- [Route](examples/route.yaml)
