# CFT Templates

This folder contains the library of templates included in the Cloud Foundation
Toolkit (henceforth, CFT).

## Overview

Each template is stored in a folder named after the templated cloud resource;
e.g., "network", "cloud_router", "healthcheck", etc. Each template folder contains:

- Readme.md - a textual description of the template's usage, prerequisites, etc.
- <resource>.py - the Python 2.7 template file
- <resource>.py.schema - the schema file associated with the template
- examples:
  - <resource>.yaml - a sample config file that utilizes the template
- tests:
  - integration:
    - <resource>.yaml - a test config file
    - <resource>.bats - a bats test harness for the test config

## Usage

??? Don't know how much of the following is relevant = given the 4 Guides we
provide (user, template developer, tool developer, and pipeline user)...
Probably none ???

The DM templates developed by this project can be used either (1) individually
via the `gloud` utility, or (2) via the Cloud Foundation tool that will be able to link
multiple unrelated templates together in order to deploy the foundation as a whole

### Deploying infrastructure with individual templates via gcloud

Each individual template has it's own usage documentation in their respective folders.
For example, `templates/cloud_router/README.md`

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
# This is my_network.yaml file
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
    --config my_network.yaml
```


### Deploying infrastructure with the Cloud Foundation Tool

Part of the Cloud Foundation Toolkit is a CLI tool (cft) that makes use of
deployment configs that have extra functionality compared to ones used by
`glcoud` to deploy resources to GCP via the Deployment Manager service.

The configs can be used with the same [template library](templates) provided with this
toolkit.

The specific configuration for each template is different, but in general
deployments via `gcloud` should be done by creating a *DM config file*
referencing the template(s), then invoking `gcloud`:

```
./src/cft create
    --config <CONFIG_1>.yaml <CONFIG_2>.yaml <CONFIG_3>.yaml
```

