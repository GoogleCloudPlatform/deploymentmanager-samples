# Internal Micro-service

## Overview
This is a [Google Cloud Deployment
Manager](https://cloud.google.com/deployment-manager/overview) template which
deploys an internally load balanced micro-service within a single zone. It uses
the existing
[internal load
balancer example](https://github.com/GoogleCloudPlatform/deploymentmanager-samples/tree/master/examples/v2/internal-lb)
and the zonal service defined in the [high-availability service
example](https://github.com/GoogleCloudPlatform/deploymentmanager-samples/tree/master/examples/v2/ha-service).

The micro-service is exposed as a service endpoint in the default network on the
project.

**NOTE**: This example uses the Service Registry API. Make sure you
enable it in your project. To use it, you may need to request access
[here](https://docs.google.com/forms/d/11SfJGB3LUGgT_aSMlVzWoJ0ec2fHKwk0J4e-zTNw0Bs/viewform?edit_requested=true).

For more details on properties of this template, see the [template
schema](microservice.py.schema).
