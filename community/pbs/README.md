Overview
========

The Portable Batch System (PBS) is designed to schedule and execute computer
tasks (jobs) on computer nodes. This document describes an approach to deploy
PBS on the Google Cloud Platform (GCP) and the deployment options that may be
selected depending on the network topology and security requirements.

Deployment Prerequisites
========================

Before starting the deployment of PBS, set up the following:

1.  [Create Organization and
    Project](https://cloud.google.com/resource-manager/docs/creating-managing-organization)
    within that organization

2.  Designate Organization Admin and the owner of the project

3.  Setup a billing account in GCP

4.  Activate necessary APIs:

    1.  gcloud services enable deploymentmanager.googleapis.com

    2.  gcloud services enable iam.googleapis.com

    3.  gcloud services enable servicemanagement.googleapis.com

5.  Define Cloud identities for users who need access to the cluster

6.  Identify [cloud service
    account](https://cloud.google.com/resource-manager/docs/access-control-proj)
    that defines the identity of the nodes (by default in the form
    \<PROJECT-NUMBER\>\@cloudservices.gserviceaccount.com e.g.
    116634650567\@cloudservices.gserviceaccount.com)

PBS Cluster Architecture
========================

We will discuss three major options for the PBS deployment:

1.  Stand-alone VPC deployment with public IP addresses for all nodes

2.  Stand-alone VPC deployment with private IP addresses for all nodes

3.  Deployment to Shared VPC with private IP addresses for all nodes

Stand-alone VPC with Public IP Addresses
----------------------------------------

The simplest possible configuration of a PBS deployment on GPC consists of a
single project with a stand-alone VPC and public IP addresses for all cluster
nodes. All PBS nodes are deployed to a single subnet within a single region and
all resources are provisioned within the same project (see diagram below). Jobs
can be submitted from the PBS controller node. The node can be accessed over the
private internet or through a VPN connection from on-prem.

This configuration is not recommended for production use cases, as it exposes
all the nodes to the internet via the public IP addresses and may pose security
concerns. The configuration, however, may work well in lab scenarios where ease
of deployment and convenience of ssh connectivity to all nodes are important
considerations.

![Standalone network with public IP addresses](https://raw.githubusercontent.com/leybzon/deploymentmanager-samples/master/community/pbs/images/standalone-public-ips.png "Img. 1")

*Diagram of a PBS deployment in a single project within a stand-alone VPC and
public IPs for all resources.*

Stand-alone VPC with Private IP Addresses
-----------------------------------------

In this configuration all PBS nodes are deployed to a single subnet within a
single project and have private IP addresses only. The PBS controller can be
used to submit jobs. The diagram below shows a case where access to the
controller from a user workstation on-prem is protected by a firewall and routed
through a VPN gateway configured within the VPC. In general, to connect to the
PBS controller or the compute instances, you can use one of the methods
described in [this
guide](https://cloud.google.com/compute/docs/instances/connecting-advanced#sshbetweeninstances).

A Cloud NAT deployed in the same region provides connectivity to the public
Internet for all nodes. That access is used for PBS software installation and
updates as well as potentially for job accessing data from the internet.

![Standalone with private IPs](https://raw.githubusercontent.com/leybzon/deploymentmanager-samples/master/community/pbs/images/standalone-private-ips.png "Img 2.")

*Diagram of a PBS deployment in a single project within a stand-alone VPC and
private IPs for all resources. Access to the internet is achieved through a
Cloud NAT.*

Deployment to shared VPC with private IP addresses
--------------------------------------------------

In this configuration, the PBS nodes are deployed in service project attached to
a VPC host project. The configuration and provisioning of the network resources
are managed in the VPC host project. In particular, the host project provisions
the subnet use for deploying PBS. The service project, in turn, uses the subnet
and hosts the PBS nodes. We assume that the service account used to deploy the
PBS nodes in the service project does not have access to provision or configure
the network resources in the VPC host project; the configuration of those
resources, therefore, should be done manually before launching the deployment
script. These resources include the host network and shared subnet, the VPN
gateway for connectivity with the on-prem network, and the Cloud NAT.

For this configuration we recommend that the PBS nodes be provisioned only with
private IP addresses (although public IPs are supported via the deployment
script). Access to the public internet is achieved via a Cloud NAT configured
(manually) in the host project. Public internet access is needed to install and
update the PBS software and potentially for jobs to access data from sources
outside of GCP.

The PBS controller can be used to submit jobs. The diagram below shows a user
workstation on the on-prem network accessing the controller via a VPN gateway.
In general, the controller can be accessed via one of the methods described in
[this
guide](https://cloud.google.com/compute/docs/instances/connecting-advanced#sshbetweeninstances).

![Shared VPC with private IPs](https://raw.githubusercontent.com/leybzon/deploymentmanager-samples/master/community/pbs/images/shared-vpc.png "Img 3.")

*Diagram of a PBS deployment in a shared VPC configuration. The PBS resources
are deployed in a service project. The project is a user of the subnet
provisioned in the host network project.*

*Access to the internet is achieved through a Cloud NAT.*

Cluster Configuration Options
=============================

This section documents the attributes available for the configuration of the
cluster deployment. They are organized as

-   Cluster Properties: attributes defining the cluster name, location, size.

-   Compute Node Properties: attributes defining the PBS version as well as the
    machine type and size of the controller and compute nodes

-   Network Properties: attributes defining the deployment of the cluster
    resources onto a network topology, such as stand-alone or shared VPC and
    private or public IPs

Cluster Properties 
-------------------

| Property          | Required / Optional | Type    | Description                                                                                                                                       |
|-------------------|---------------------|---------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| cluster_name      | required            | String  | Name of the cluster                                                                                                                               |
| region            | required            | String  | Region where the PBS instances are provisioned                                                                                                    |
| zone              | required            | String  | Zone where the PBS instances are provisioned                                                                                                      |
| static_node_count | required            | Integer | Number of compute nodes created for the cluster                                                                                                   |
| prefix            | optional            | String  | Prefix of the names of the instances and other resources in the cluster. Used to distinguish different clusters deployed within the same project. |
| service_account   | optional            | String  | Service account email |

Compute Node Properties
-----------------------

| Property                | Required / Optional | Type    | Description                                                                                                                                                                                                                      |
|-------------------------|---------------------|---------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| compute_machine_type    | required            | String  | Machine type for compute node instances, eg. n1-standard-4                                                                                                                                                                       |
| compute_disk_type       | optional            | String  | Disk type (pd-ssd or pd-standard) for the compute nodes. Default: pd-standard                                                                                                                                                    |
| compute_disk_size_gb    | optional            | Integer | Size of disk for the compute nodes in [GB]. Default: 100GB                                                                                                                                                                       |
| controller_machine_type | required            | String  | Machine type to use for the controller instance, eg. n1-standard-4                                                                                                                                                               |
| controller_disk_type    | optional            | String  | Disk type (pd-ssd or pd-standard) for the controller instance. Default: pd-standard                                                                                                                                              |
| controller_disk_size_gb | optional            | Integer | Size of disk for the controller instance. Default: 100GB                                                                                                                                                                         |
| compute_image           | optional            | String  | Pre-configured PBS compute node image. If this property is specified, the image is used for the provisioning of the compute instances                                                                                            |
| controller_image        | optional            | String  | Pre-configured PBS controller image, used for the provisioning of the controller instance                                                                                                                                        |
| pbs_version             | optional            | String  | Version of PBS software to be installed in the cluster. Please check <http://community.pbspro.org/c/announcements> and <https://github.com/PBSPro/pbspro/releases> for the information about the latest version of the software. |

Network Properties
------------------

| Property            | Required / Optional | Type    | Description                                                                                                                                                                                                                             |
|---------------------|---------------------|---------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| cidr                | optional            | String  | RFC1918 subnet to run the PBS instances Default: "10.10.0.0/16"                                                                                                                                                                         |
| network             | optional            | String  | Name of the external network to be used in the deployment. This parameter is required only if the existing_network parameter below is set to true; ignored otherwise.                                                                   |
| existing_network    | optional            | Boolean | If set to "true", the cluster will be configured to use an already created network with the name taken from the "network" attribute. If set to "false", a new network will be created for the deployment of the cluster. Note that correct routing for the internet traffic between network and the Internet should be configured prior to the deployment if "existing_network " is set to true. Default: false |
| vpc_hosting_project | optional            | String  | Name of the project that hosts the network.                                                                                                                                                                                             |
| subnet              | optional            | String  | External network subnet used for deployment of the PBS nodes. The parameter is used and required only if existing_network is set to true                                                                                                |
| compute_public_ips  | optional            | Boolean | Whether nodes are assigned public IPs or not. If set to "false", the nodes will use Cloud NAT for Internet access. Default: true                                                                                                        |

Examples of cluster configurations
==================================

This section provides examples of typical cluster configurations. It specifies
the YAML deployment files and the expected resource setup for the most complex
network topologies (shared VPC).

For the shared VPC configuration, we assume that the service account used to
deploy the cluster on the service project does not have the privileges to
provision resources on the host VPC project; therefore, we document the expected
setup of those resources (firewalls, routes, etc.) in the host VPC project and
will not attempt to provision them via the script.

### Stand Alone Network, public IPs

This yaml configuration example is used to deploy the PBS cluster in a stand
alone VPC network, automatically provisioned. All nodes in the cluster will have
public IP addresses.

```yaml

imports:
- path: pbs.jinja

resources:
- name: pbs-cluster
  type: pbs.jinja
  properties:
    cluster_name            : google
    static_node_count    : 2
    zone                         : us-west2-b
    region                       : us-west2

    controller_machine_type : n1-standard-2
    compute_machine_type  : n1-standard-2
    pbs_version             : 18.1.2

```


### Standalone network, private IPs

This yaml configuration example deploys a PBS cluster in a stand alone VPC,
automatically provisioned. All compute nodes have only private IP addresses. Compute
nodes access the internet through a Cloud NAT configuration.

The PBS controller can be used to submit jobs. In general, it can be accessed
via one of the methods described in [this
guide](https://cloud.google.com/compute/docs/instances/connecting-advanced#sshbetweeninstances).
If it is an option, you can test this configuration by provisioning a VM to act
as a bastion host in the same subnet as the cluster (e.g. 10.10.0.0/16) and also
a public IP address. You can then log into the bastion host and create local ssh
keys with the ssh-keygen command (e.g. ssh-keygen -t rsa -b 4096 -C
"username\@example.com"). By default, the generated public key is in the file
\~/.ssh/id_rsa.pub . The content of the public key can be added to the "SSH
Keys" section of the compute engine metadata for the project (e.g. pbs-project)
(note to remove all newline characters if cutting and pasting the public key).
You can then ssh from the bastion to the controller.


YAML Script Example:
```yaml
imports:
- path: pbs.jinja

resources:
- name: pbs-cluster
  type:   pbs.jinja
  properties:
    cluster_name            : google
    static_node_count    : 2
    region                       : us-central1
    zone                         : us-central1-a

    controller_machine_type : n1-standard-2
    compute_machine_type  : n1-standard-2
    pbs_version              : 18.1.2

    compute_public_ips  : false
    prefix                  : cluster26-
```

### Shared Network, all private IPs

This example yaml configuration deploys a PBS cluster in an existing subnet
(pbs-subnet) created on a shared host VPC for PBS. In the example below, the
network named pbs-host-network and the subnet pbs-subnet are created in the host
project hpc-host-network-project prior to the cluster installation. Please refer
to the [Provisioning Shared
VPC](https://cloud.google.com/vpc/docs/provisioning-shared-vpc) document for
more details on the configuration and permissions needed for the shared network
setup. Note that it is possible to provision a shared VPC using a separate
deployment script as described in [this
document](https://github.com/GoogleCloudPlatform/deploymentmanager-samples/tree/master/examples/v2/project_creation)
.

In this configuration, all of the nodes will have only private IP addresses. The
PBS controller can be used to submit jobs. In general, it can be accessed via
one of the methods described in [this
guide](https://cloud.google.com/compute/docs/instances/connecting-advanced#sshbetweeninstances).
If it is an option, you can test this configuration by provisioning a VM to act
as a bastion host in the same subnet as the cluster (pbs-subnet) and also a
public IP address. You can then log into the bastion host and create local ssh
keys with the ssh-keygen command (e.g. ssh-keygen -t rsa -b 4096 -C
"username\@example.com"). By default, the generated public key is in the file
\~/.ssh/id_rsa.pub . The content of the public key can be added to the "SSH
Keys" section of the compute engine metadata for the service project (e.g.
pbs-project) (note to remove all newline characters if cutting and pasting the
public key). You can then ssh from the bastion to the controller.

**Prerequisites**

Note that the following resources should be configured prior to the deployment
of PBS on the shared VPC network:

-   Two projects should be created

    -   The service project to host the compute and controller nodes e.g.
        pbs-project

    -   The network host project, where the shared VPC is configured e.g.
        hpc-host-network-project

-   The shared VPC subnet should be configured on the host project e.g.
    pbs-host-network

-   The service account used to provision the VM in the service project should
    be granted role networkUser. By default the account is
    \<SERVICE-PROJECT-ID\>\@cloudservices.gserviceaccount.com e.g.
    116666750567\@cloudservices.gserviceaccount.com

-   Create a [Cloud NAT](https://cloud.google.com/nat/docs/overview) in the VPC
    host project for the VPC. The following parameters are examples; the actual
    values depend on the name (and region) of your host network.

    -   Gateway name: hpc-host-network-central1-nat

    -   VPC network: (example) pbs-host-network

    -   Region: (example) us-central1

    -   Cloud router: create new accepting the defaults for network and region

    -   NAT mapping section: accept all defaults

	For the convinience of deploying network resources on the shared VPC, a separate GCP [deployment script](host-network/) can be used. 

-   [VPC Firewall](https://cloud.google.com/vpc/docs/firewalls) should be
    configured to enable port 22 ingress access in order to connect to the
    controller instance. Also Internal access between the PBS nodes should also
    be enabled in order to provide internal PBS communication. Please see the
    table below for details about firewall configuration:

|   | Name                 | Type    | Targets      | Filters              | Protocols / ports | Action | Priority | Network          |
|---|----------------------|---------|--------------|----------------------|-------------------|--------|----------|------------------|
|   | pbs-network-internal | Ingress | Apply to all | Subnets: pbs-subnet  | all               | Allow  | 1000     | pbs-host-network |
|   | pbs-subnet-fw        | Ingress | Apply to all | IP ranges: 0.0.0.0/0 | tcp:22 icmp       | Allow  | 1000     | pbs-host-network |

YAML Script Example:

```yaml
imports:
- path: pbs.jinja

resources:
- name: pbs-cluster
  type: pbs.jinja
  properties:
    cluster_name            : google
    static_node_count    : 2
    region                       : us-central1
    zone                         : us-central1-a

    controller_machine_type : n1-standard-2
    compute_machine_type  : n1-standard-2
    pbs_version             : 18.1.2

    existing_network      : true
    network                    : pbs-host-network
    subnet                      : pbs-subnet
    vpc_hosting_project : hpc-host-network-project
    compute_public_ips : false
```

Storage Considerations
======================

This deployment of PBS requires a shared file system between the controller
(submit node) and the compute nodes. By default, it is implemented by sharing
the local disk of the controller as an NFS export. For production grade
deployments, this setup might need to be replaced with other file storage
technologies, such as Cloud Filestore, Elastifile, Quobytes, or a deployment of
[Lustre](https://en.wikipedia.org/wiki/Lustre_(file_system)), to name a few
options.

When selecting local disks for the controller and compute nodes, the following
options should be considered: [Persistent
Disk](https://cloud.google.com/persistent-disk/) and [Local
SSD](https://cloud.google.com/compute/docs/disks/#localssds).

While local SSD provides the best possible performance in terms of latency and
throughput, data on local disks is not persisted upon instance termination. That
may bring the requirement for additional data synchronization or replication
processes. An additional limitation of local SSDs is size, currently limited to
3TB distributed over 8 disks attached to the instance.

Persistent disks provide scalable block-storage solution, intended for use as
attached volumes or point-in-time snapshots. Persistent disk can be mounted to
in read and write mode to single instance or can be mounted in read-only mode to
multiple nodes. The size of persistent disks is limited to 64TB

How to use deployment manager to create a cluster
=================================================

The command [gcloud create
deployment](https://cloud.google.com/deployment-manager/docs/deployments/) is
used to deploy the PBS cluster on GCP. In the case of the shared VPC
configuration, it should deploy resources in the service project.

To deploy cluster to GCP, you can run the following command:

*gcloud deployment-manager deployments --project=[project name] create
[deployment name]*

*--config pbs-cluster.yaml*

For example: *gcloud deployment-manager deployments --project=pbs-project create
pbs142 --config pbs-cluster.yaml*

How to use deployment manager to delete a cluster
=================================================

The command [gcloud delete
deployment](https://cloud.google.com/sdk/gcloud/reference/deployment-manager/deployments/delete)
is used to delete GCP resources associated with the cluster

To delete PBS cluster, please run the following command:

*gcloud deployment-manager deployments delete --project=[project name]
[deployment name]*

Example:

*gcloud deployment-manager deployments delete --project=hpc-playground-223721
pbs141*

Validation and testing PBS Cluster 
===================================

In order to check the status of PBS cluster, the following command can be used:

pbsnodes -a

If the nodes are up and the controller can successfully communicate to the
compute nodes, the command above will produce an output similar to this:

```
test9-compute1

Mom = test9-compute1.us-west2-b.c.hpc-playground-223721.internal

ntype = PBS

state = free

pcpus = 2

resources_available.arch = linux

resources_available.host = test9-compute1

resources_available.mem = 7493208kb

resources_available.ncpus = 2

resources_available.vnode = test9-compute1

resources_assigned.accelerator_memory = 0kb

resources_assigned.hbmem = 0kb

resources_assigned.mem = 0kb

resources_assigned.naccelerators = 0

resources_assigned.ncpus = 0

resources_assigned.vmem = 0kb

resv_enable = True

sharing = default_shared

last_state_change_time = Fri Dec 21 09:46:36 2018

test9-compute2

Mom = test9-compute2.us-west2-b.c.hpc-playground-223721.internal

ntype = PBS

state = free

```

The state of all nodes should be "free" prior to any jobs submitted to the
cluster.

Software Components and Templates 
==================================

| pbs-cluster.yaml  | Configuration file that describes cluster configuration                                                                                                                                                      |
|-------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| pbs.jinja         | Deployment [configuration](https://cloud.google.com/deployment-manager/docs/configuration/)                                                                                                                  |
| pbs.jinja.schema  | [Specification](https://cloud.google.com/deployment-manager/docs/configuration/templates/using-schemas) of deployment, a set of rules that a configuration file must meet in order to use pbs.jinja template |
| startup-script.py | Script to be executed when compute instance is started. Includes commands to configure PBS nodes                                                                                                             |

Conclusions
===========

We discussed three options for deploying an Open PBS cluster on GCP. Due to the
nature of the cloud platform, it is relatively easy to select appropriate
machine types and determine the number of nodes required to perform
calculations. Also, use of deployment manager templates simplifies bringing up
compute cluster and shutting them down as needed.
