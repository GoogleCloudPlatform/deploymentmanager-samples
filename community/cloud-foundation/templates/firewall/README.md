# Firewall

This template creates firewall rules for a network.

## Prerequisites

- Install [gcloud](https://cloud.google.com/sdk)
- Create a [GCP project, set up billing, enable requisite APIs](../project/README.md)
- Create a [network](../network/README.md)
- ??? roles/permissions ???

## Deployment

### Resources

- [compute.beta.firewall](https://cloud.google.com/compute/docs/reference/rest/beta/firewalls)
  
  **Note:** The beta API supports the firewall log feature.

### Properties

See `properties` section in the schema file(s):

-  [Firewall](firewall.py.schema)

### Usage

1. Clone the [Deployment Manager samples repository](https://github.com/GoogleCloudPlatform/deploymentmanager-samples):

```
    git clone https://github.com/GoogleCloudPlatform/deploymentmanager-samples
```

2. Go to the [community/cloud-foundation](../../) directory:

```
    cd community/cloud-foundation
```

3. Copy the example DM config to be used as a model for the deployment; in this case, [examples/firewall.yaml](examples/firewall.yaml):

```
    cp templates/firewall/examples/firewall.yaml my_firewall.yaml
```

4. Change the values in the config file to match your specific GCP setup (for properties, refer to the schema files listed above):

```
    vim my_firewall.yaml  # <== change values to match your GCP setup
```

5. Create your deployment (replace <YOUR_DEPLOYMENT_NAME> with the relevant deployment name):

```
    gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config my_firewall.yaml
```

6. In case you need to delete your deployment:

```
    gcloud deployment-manager deployments delete <YOUR_DEPLOYMENT_NAME>
```

## Examples

- [Firewall](examples/firewall.yaml)
