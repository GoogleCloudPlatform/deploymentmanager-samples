# Cloud Foundation Toolkit Project

This project aims to provide a number of high-quality, production-ready GCP
Deployment Manager templates, tools, example usage and documentation to help
enterprises to create their foundational infrastructure in Google Cloud.


## Usage

The DM templates developed by this project can be used either (1) individually
via the `gloud` utility, or (2) via the Cloud Foundation tool that will be able to link
multiple unrelated templates together in order to deploy the foundation as a whole

### Deploying infrastructure with individual templates via gcloud

Each individual template has it's own usage documentation
[here](docs/templates/).

The specific configuration for each template is different, but in general
deployments via `gcloud` should be done by creating a *DM config file*
referencing the template(s), then invoking `gcloud`:

```
gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config <YOUR_DEPLOYMENT_CONFIG>.yaml
```

As an example, to create a simple network with the `network.py` template, create
a deployment config file:

```
# This is my-network.yaml file
imports:
  - path: templates/network.py

resources:
  - name: my-network
    type: templates/network.py
    properties:
      name: my-network
      autoCreateSubnetworks: true
```

The properties, required and optional, defined by the `network.py` template can
be found in the schema file associated with the template: `network.py.schema`.
These properties can be tweaked to implement infrastructure that are specific
to a particular enterprise.

Once the deployment config is ready, think of a name for your deployment, say,
`my-network-deployment` and execute `gcloud`, giving the name and config file
as arguments:

```
gcloud deployment-manager deployments create my-network-deployment \
    --config my-network.yaml
```


### Deploying infrastructure with the Cloud Foundation tool

**TO BE IMPLEMENTED**


## Contributing

Detailed information on contributing and developing can be found
[here](docs/development.md)


## Testing

Detailed information on testing can be found [here](docs/testing.md)


## License

Apache 2.0 - See [LICENSE](LICENSE) for more information.

