# Cloud Router

Templated Cloud Router deployment

## Prerequisites
- Install [gcloud](https://cloud.google.com/sdk)
- Create a [GCP project, setup billing, enable requisite APIs](docs/templates/project.md)


## Deployment

### Resources

- [compute.v1.router](https://cloud.google.com/compute/docs/reference/rest/v1/routers)


### Properties

See `properties` section in the schema files

-  [Cloud Router](../../templates/cloud_router.py.schema)


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


## Examples

- [Cloud Router](../examples/cloud_router.yaml)
