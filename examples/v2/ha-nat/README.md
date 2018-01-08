# ​HA/High​ ​Bandwidth​ ​NAT​ ​Gateways

Instances created with no public IP address are not able to connect to the internet. To allow access a NAT service has to be
 created inside GCP.

## Overview
This is a [Google Cloud DeploymentManager](https://cloud.google.com/deployment-manager/overview) template which
deploys a high-availabe NAT service to multiple zones in a single region. 

The script creates three instance groups with one instance each. Each instance group is based on an instance template with auto-healing capabilities. The instnaces of the instance groups are connected with the outside world via public IPs. Routes are created to forward traffic from instances with internal IPs to the created NAT VMs.

To mark an instance to route its traffic via the NAT service it must be tagged with the "no-ip" tag (see below).

## Properties
The HA service takes the following input properties:

* `region`: the region where the service should be deployed to.
* `zone_[1-3]`: the zones the three instance groups should be deployed to.
* `internalIP_[1-3]`: the internal IP addresses .

For more details on configuration of this template, see [HA-NAT.yaml](HA-NAT.yaml).

## Architecture
The template architecture for this configuration looks like this:

```
HA-NAT.yaml.yaml
 |
 |- HA-NAT.jinja
     |
     |- instanceTemplate.jinja
     |
     |- instanceGroup.jinja (zone1)
     |
     |- instanceGroup.jinja (zone2)
     |
     |- instanceGroup.jinja (zone3)
     |
     |- route.jinja (zone1)
     |
     |- route.jinja (zone2)
     |
     |- route.jinja (zone3)
```

## Deploy & Test the service

Before deployment you need to adjust the following settings in [HA-NAT.yaml](HA-NAT.yaml) to your environment.

In the example below internal IPs come frome the CIDR range of the [default network for the corresponding region](https://cloud.google.com/vpc/docs/vpc#ip-ranges). 

```YAML
    # settings to adjust
    region: europe-west1
    zone_1: europe-west1-b
    zone_2: europe-west1-c
    zone_3: europe-west1-d
    # CIDR range 10.132.0.0/20 of europe-west1
    internalIP_1: 10.132.0.2
    internalIP_2: 10.132.0.3
    internalIP_3: 10.132.0.4
```

### Deploy
`gcloud deployment-manager deployments create ha-nat-v1 --config HA-NAT.yaml`

### Test it

Add two VMs with no external IP (can't communicate with internet)
`gcloud compute instances create vm1 vm2 --no-address`

Create third VM to use as jumphost to access internal VMs
`gcloud compute instances create vm3`

#### Add NAT tag to vm1
This will allow vm1 to connect to the internet via the NAT service.
`gcloud compute instances add-tags vm1 --tags no-ip`

#### Connect to natted VM
SSH to vm3
`gcloud beta compute ssh vm3`

Authenticate vm3 to be able to login to vm1 / vm2
`gcloud auth login`

SSH to vm1 from vm3
`gcloud beta compute ssh vm1 --internal-ip`

Test connection works
`ping 8.8.8.8`

#### Connect to unnatted VM
SSH to vm3
`gcloud beta compute ssh vm3`

SSH to vm2 from vm3
`gcloud beta compute ssh vm2 --internal-ip`

Test connection does not work
`ping 8.8.8.8`

#### Test delete one of NAT servers

You can see how the NAT service still works without interruption.
`gcloud compute instances list | grep nat-1 | cut -d ' ' -f 1 | xargs gcloud compute instances delete --quiet`

### Remove NAT tag
`gcloud compute instances remove-tags vm1 --tags=no-ip`

### Undeploy
`gcloud deployment-manager deployments delete ha-nat-v1`

## Important commands

### Preview
`gcloud deployment-manager deployments create ha-nat-v1 --config HA-NAT.yaml --preview`


## Links
 - [Overview of API Endpoints](https://cloud.google.com/deployment-manager/docs/configuration/supported-resource-types)