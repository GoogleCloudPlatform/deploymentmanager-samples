# Networks and subnets

Templated network and subnet deployment

## Prerequisites
- Install [gcloud](https://cloud.google.com/sdk)
- Create a [GCP project, setup billing, enable requisite APIs](docs/templates/project.md)


## Deployment

### Resources

- [compute.v1.network](https://cloud.google.com/compute/docs/reference/latest/networks)
- [compute.v1.subnetwork](https://cloud.google.com/compute/docs/reference/latest/subnetworks)


### Properties

See `properties` section in the schema files

-  [network](../../templates/network.py.schema)
-  [subnetwork](../../templates/subnetwork.py.schema)


### Deployment

#### Create

```
gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config <YOUR_DEPLOYMENT_CONFIG>.yaml
```


#### Delete

```
gcloud deployment-manager deployments delete <YOUR_DEPLOYMENT_NAME>
```
