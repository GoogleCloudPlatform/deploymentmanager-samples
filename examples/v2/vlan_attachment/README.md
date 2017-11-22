# VLAN Attachment Example

## Overview

This is a [Google Cloud Deployment
Manager](https://cloud.google.com/deployment-manager/overview) template that
deploys a new [Cloud Router](https://cloud.google.com/router/docs/how-to/creating-routers), creates a [VLAN attachment](https://cloud.google.com/interconnect/docs/how-to/dedicated/creating-vlan-attachments), adds an interface to the Cloud Router and adds a BGP peer to the interface .

## IAM setup
If you are creating a VLAN attachment not in the same project where your interconnect is, i.e. <vpc_project_id> != <interconnect_project_id>, make sure that Deployment Manager's service account <vpc_project_number>@cloudservices.gserviceaccount.com has the following permissions assigned in  interconnect_project_id project:
* compute.interconnects.use 
* resourcemanager.projects.get 

Both permissions are available in the "Compute Network User" role, please consider assigning this role (or any other roles with these permissions) to the service account.

## Deploy the template

1. Change values of properties in  `vlan_attachment.yaml`, do not uncomment peer_ip_address property yet

2. Deploy with the following command:

    gcloud deployment-manager deployments create <your_deployment_name> --config ./vlan_attachment.yaml

3. Find customer_router_ip output value by [viewing the configuration layout](https://cloud.google.com/deployment-manager/docs/deployments/viewing-manifest#configuration_layout) or by executing a script that returns outputs associated with the deployment:

	./display_outputs.sh <your_deployment_name> 

4. Uncomment peer_ip_address property in `vlan_attachment.yaml` and set it's value to the IP address part of  customer_router_ip (e.g. if customer_router_ip is 169.254.68.162/29, use 169.254.68.162 as a value)

5. Update the deployment with the following command:

    gcloud deployment-manager deployments update <your_deployment_name> --config ./vlan_attachment.yaml


## More information

[Cloud Interconnect Documentation](https://cloud.google.com/interconnect/docs/)
