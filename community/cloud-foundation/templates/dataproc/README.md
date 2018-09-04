# Dataproc

This template creates Dataproc cluster.

## Prerequisites

- Install [gcloud](https://cloud.google.com/sdk)
- Create a [GCP project, set up billing, enable requisite APIs](../project/README.md)
- Enable [Cloud Dataproc API](https://cloud.google.com/dataproc/docs/reference/rest/)
- Make sure that the default service account has the following permissions:
    - dataproc.agents.create
    - dataproc.agents.get
    - dataproc.agents.update
    - dataproc.tasks.lease
    - dataproc.tasks.listInvalidatedLeases
    - dataproc.tasks.reportStatus,
  or a Dataproc Worker (`roles/dataproc.worker`) role. Alternatively, create a new
  service account with the above permissions/roles, and add it to the template's
  `resources.properties.serviceAccountEmail` property.

## Deployment

### Resources

- [compute.v1.instance](https://cloud.google.com/compute/docs/reference/rest/v1/instances)
- [compute.v1.instanceTemplate](https://cloud.google.com/compute/docs/reference/latest/instanceTemplates)
- [compute.v1.instanceGroup](https://cloud.google.com/compute/docs/reference/latest/instanceGroups)
- [dataproc.v1.cluster](https://cloud.google.com/dataproc/docs/reference/rest/v1/projects.regions.clusters)

### Properties

See the `properties` section in the schema file(s):
- [Dataproc](dataproc.py.schema)

### Usage

1. Clone the [DM Samples repository](https://github.com/GoogleCloudPlatform/deploymentmanager-samples):

```
    git clone https://github.com/GoogleCloudPlatform/deploymentmanager-samples
```

2. Go to the [community/cloud-foundation](../../) directory:

```
    cd community/cloud-foundation
```

3. Copy the example DM config to be used as a model for the deployment; in this case, [examples/dataproc.yaml](examples/dataproc.yaml):

```
    cp templates/dataproc/examples/dataproc.yaml my_dataproc.yaml
```

4. Change the values in the config file to match your specific GCP setup (for properties, refer to the schema files listed above):

```
    vim my_dataproc.yaml  # <== change values to match your GCP setup
```

5. Create your deployment (replace <YOUR_DEPLOYMENT_NAME> with the relevant deployment name):

```
    gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config my_dataproc.yaml
```

6. In case you need to delete your deployment:

```
    gcloud deployment-manager deployments delete <YOUR_DEPLOYMENT_NAME>
```

## Examples

- Creating a [Dataproc cluster](examples/dataproc.yaml)
