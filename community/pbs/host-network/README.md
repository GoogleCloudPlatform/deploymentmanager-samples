Overview
========

Deployment of Portable Batch System (PBS) into the [shared VPC](https://cloud.google.com/vpc/docs/shared-vpc) environment requires proper configuration of the host project VPC in addition to configuration of service project VPC. Deployment scripts in this project provision resources needed to support PBS in the host project. 

  
Deployment Prerequisites
========================

Before starting the deployment of PBS, set up the following:

1.  [Create Organization](https://cloud.google.com/resource-manager/docs/creating-managing-organization) for the host project
    unless organization was already created.
	
2.  [Designate Organization Admin](https://cloud.google.com/resource-manager/docs/creating-managing-organization#adding_an_organization_admin) and the owner of the project

3.  [Setup a billing account](https://cloud.google.com/billing/docs/how-to/manage-billing-account) for the Organization

4.  Activate necessary APIs:

    1.  gcloud services enable deploymentmanager.googleapis.com

    2.  gcloud services enable iam.googleapis.com

    3.  gcloud services enable servicemanagement.googleapis.com

5.  Define [cloud identities](https://cloud.google.com/identity/) for users who need access to the cluster

6.  Identify [cloud service
    account](https://cloud.google.com/resource-manager/docs/access-control-proj)
    that defines the identity of the nodes (by default in the form
    \<PROJECT-NUMBER\>\@cloudservices.gserviceaccount.com e.g.
    116634650567\@cloudservices.gserviceaccount.com)
6. Provision VPC and subnet in the host project as described in [Provisioning Shared VPC documentation](https://cloud.google.com/vpc/docs/provisioning-shared-vpc)

Deployment Steps
================

1.  Update parameters of pbs-cluster-host.yaml file to match name of the shared VPC and region where VPC is deployed
2.  Run deployment manager command with pbs-cluster-host.yaml

Configuration options
---------------------

| Property          | Required / Optional | Type    | Description                                                                                                                                       |
|-------------------|---------------------|---------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| region            | required            | String  | Region where the PBS instances will be provisioned                                                                                                |
| prefix            | optional            | String  | Prefix of the names of the instances and other resources in the cluster. Used to distinguish different clusters deployed within the same project. |
| cidr              | optional            | String  | RFC1918 subnet to run the PBS instances Default: "10.10.0.0/16"                                                                                   |
| network           | requred             | String  | Name of the network to be used in the deployment.                                                                                                 |
| vpc_hosting_project | requred           | String  | Name of the project that hosts the VPC network (current project).                                                                                 |

Example of configuration file
==================================

```yaml
imports:
- path: pbs-host.jinja

resources:
- name: pbs-cluster-host
  type:   pbs-host.jinja
  properties:
    cluster_name         : google
    region               : us-central1
    zone                 : us-central1-a
    cidr                 : 10.8.0.0/14

    network              : shared-vpc-host-network
    subnet               : pbs-subnet
    vpc_hosting_project  : host-net-project

    prefix               : cluster01-
```


Example of deployent command
==================================
```
gcloud deployment-manager deployments  --project=host-net-project  create deployment1 --config pbs-cluster-host.yaml
```