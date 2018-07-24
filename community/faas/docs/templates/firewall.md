# Firewalls

Templated firewall rules

## Prerequisites

- Install [gcloud](https://cloud.google.com/sdk)
- Create a [GCP project, setup billing, enable requisite APIs](docs/templates/project.md)
- Create a [network](docs/templates/network.md)

## Deployment

### Resources

- [compute.beta.firewall](https://cloud.google.com/compute/docs/reference/rest/beta/firewalls)


### Properties

See `properties` section in the schema files

-  [firewall](../../templates/firewall.py.schema)


### Deployment

#### Usage

1. Clone the [DM Samples_repository](https://github.com/GoogleCloudPlatform/deploymentmanager-sample)
2. Go to the [community/faas](community/faas) directory
3. Copy the example DM config to be used as a model for the deployment, in this case [examples/firewall.yaml](examples/firewall.yaml)
4. Change the values in the config file to match your specific GCP setup.
   Refer to the properties in the schema files described above.
5. Create your deployment as described below, replacing <YOUR_DEPLOYMENT_NAME>
   with your with your own deployment name


For example:

```
git clone https://github.com/GoogleCloudPlatform/deploymentmanager-sample
cd community/faas
cp examples/firewall.yaml my-firewall.yaml
vim my-firewall.yaml  # <== change values to match your GCP setup
gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config my-firewall.yaml
```

#### Create

```
gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config firewall.yaml
```


#### Delete

```
gcloud deployment-manager deployments delete <YOUR_DEPLOYMENT_NAME>
```


## Examples

- [Firewall](../examples/firewall.yaml)
