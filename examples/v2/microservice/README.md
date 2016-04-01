# Internal Micro-service

## Overview
This is a [Google Cloud Deployment
Manager](https://cloud.google.com/deployment-manager/overview) template which
deploys an internally load balanced micro-service within a single zone. It uses
the existing
[internal load
balancer example](https://github.com/GoogleCloudPlatform/deploymentmanager-samples/tree/master/examples/v2/internal-lb)
and the zonal service defined in the [HA service
example](https://github.com/GoogleCloudPlatform/deploymentmanager-samples/tree/master/examples/v2/ha-service).

The micro-service is exposed as a service endpoint in the default network on the
project.

**NOTE**: This example makes use of the Service Registry API. You may need to
request access to this Alpha API.

For more details on properties of this template, see the [template
schema](microservice.py.schema).
