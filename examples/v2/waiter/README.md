# Waiter Example

## Overview
This is a [Google Cloud Deployment
Manager](https://cloud.google.com/deployment-manager/overview) template that
deploys a VM instance, a RuntimeConfig resource, and a Waiter
resource. The Waiter is a resource that causes the deployment to block
until receiving a signal. In most cases, the signal will be generated
by a VM instance within the same deployment after some stage has
completed. For example, a Waiter can be used to prevent a deployment
from finishing until a service deployed to a VM instance has started
and is ready to handle requests.

To signal a Waiter, the VM creates a Variable resource. The Waiter
monitors its parent RuntimeConfig for variables created in a
location defined in its configuration. Depending on their location,
variables can indicate operation success or failure. Waiters can be
configured to wait for multiple signals before succeeding or failing.

## Deploy the template
Use `config.yaml` to deploy this example template. Before deploying,
edit the file and specify the zone in which to create the VM instance.

When ready, deploy with the following command:

    gcloud deployment-manager deployments create waiter --config config.yaml


## More information

The RuntimeConfig, Waiter, and Variable resource types are part of the
Deployment Manager RuntimeConfig API. More information is available at
https://cloud.google.com/deployment-manager/runtime-configurator.
