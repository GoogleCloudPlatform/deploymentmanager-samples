# VLAN Attachment Example

## Overview

This is a [Google Cloud Deployment
Manager](https://cloud.google.com/deployment-manager/overview) template that
deploys a new [Cloud Router](https://cloud.google.com/router/docs/how-to/creating-routers), creates [VLAN attachment] (https://cloud.google.com/interconnect/docs/how-to/dedicated/creating-vlan-attachments),  adds an interface to the Cloud Router and adds a BGP peer to the interface .

## IAM setup
If you are creating a VLAN attachment not in the same project where Interconnect is, i.e. vpc_project_id != interconnect_project_id, make sure that deployment manager's service account <VPC_PROJECT_NUMBER>@cloudservices.gserviceaccount.com has the following permissions assigned in  interconnect_project_id project:
 - compute.interconnects.use 
 - resourcemanager.projects.get 
Both permissions are available in the "Compute Network User" role, please consider assigning this role (or any other roles with these permissions) to the service account.

## Deploy the template

Use `vlan_attachment.yaml` to deploy this example template after changing values of the properties.

When ready, deploy with the following command:

    gcloud deployment-manager deployments create demo-vlan-attachment --config ./vlan_attachment.yaml

## More information

[Cloud Interconnect Documentation](https://cloud.google.com/interconnect/docs/)
