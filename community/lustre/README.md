# Lustre Deployment Manager Script

This is a Deployment Manager script to deploy a Lustre parallel file system cluster on Google Cloud Platform. This tool deploys the open source Lustre RPMs available on whamcloud.com.

This script deploys a MDS/MGS combined node, and N OSS nodes. On both node types the IP addresses, machine type, disk type, and disk size are all configurable in the lustre.yaml file.

Please note: This software is provided as-is, with no guarantees of support. This is an example script, and should be used as such.

## Configuration

These scripts are configured using the lustre.yaml configuration file. This file has the following fields. The fields in bold are required, all others are optional. A short description and example inputs can also be found in the lustre-template.yaml file.

#### Cluster Configuration
* **cluster_name** - Name of the Lustre cluster, prepends all deployed resources
* **zone** - Zone to deploy the cluster into
* **cidr** - IP range in CIDR format
* **external_ips** - True/False, Lustre nodes have external IP addresses. If false then a Cloud NAT is setup as a NAT gateway
* vpc_net - Define this field, and the vpc_subnet field, to deploy the Lustre cluster to an existing VPC
* vpc_subnet - Existing VPC subnet to deploy Lustre cluster to
* shared_vpc_host_proj - Defien this field, as well as the vpc_net and vpc_subnet fields, to deploy the cluster to a Shared VPC

#### Filesystem Configuration
* fs_name - Lustre filesystem name
* lustre_version - Lustre version to deploy, use "latest-release" to get the latest branch from downloads.whamcloud.com/public/lustre/
* e2fs_version - E2fsprogs version to deploy,  use "latest" to get the latest branch from downloads.whamcloud.com/public/e2fsprogs/

#### MDS/MGS Configuration
* mds_ip_address - Internal IP Address to specify for MDS/MGS node
* mds_machine_type - Machine type to use for MDS/MGS node (see (https://cloud.google.com/compute/docs/machine-types)[https://cloud.google.com/compute/docs/machine-types])
* mds_disk_type - Disk type to use for the MDS/MGS boot disk (pd-standard or pd-ssd)
* mds_disk_size_gb - Size of MDS boot disk in GB
* **mdt_disk_type** - Disk type to use for the Metadata Target (MDT) disk
* **mdt_disk_size_gb** - Size of MDT disk in GB

#### OSS Configuration
* **oss_node_count** - Number of Object Storage Server (OSS) nodes to create
* oss_ip_range_start - Start of the IP range for the OSS node(s). If not specified, use automatic IP assignment
* oss_machine_type - Machine type to use for OSS node(s)
* oss_disk_type - Disk type to use for the OSS boot disk
* oss_disk_size_gb - Size of MDS boot disk in GB
* **ost_disk_type** - Disk type to use for the Object Storage Target (OST) disk
* **ost_disk_size_gb** - Size of OST disk in GB

## Launch the Lustre Cluster

Once you've customized the lustre.yaml file and completed all the required fields, and ensured you have adequate [resource quota](https://cloud.google.com/compute/quotas), you are ready to launch your Lustre cluster.

Use the following command to launch your Lustre cluster.

    gcloud deployment-manager deployments create lustre --config lustre.yaml

Once the cluster is deployed, ssh in to the MDS instance. You may notice a message indicating that the Lustre filesystem is still being installed, and that you will be notified when the process is complete. Please wait until you see a second message reporting the installation complete, and providing the sample mount command for your cluster.

## Mount the Lustre filesystem

Once the nodes are installed and the filesystem is online you're ready to mount your clients. Install the [Lustre client software](http://wiki.lustre.org/Installing_the_Lustre_Software#Lustre_Client_Software_Installation) on an instance that is routable to the Lustre cluster's subnet. Once installed, and with the Lustre module loaded, use the following mount command to mount your filesystem:

    mount -t lustre < MDS #1 Hostname >:< MDS #N Hostname >:/< FS NAME > < LOCAL MOUNT >

An example would be:

    mount -t lustre lustre-mds1:/lustre /mnt/lustre

You may use the Lustre Metadata Server (MDS) to test if the clients can mount the filesystem. However, please do not leave the filesystem mounted on the MDS server as it may cause filesystem corruption.

Once the filesystem is mounted you will see no output returned with the mount command. You can verify the filesystem is mounted by checking the "mount" command, and by running "lctl dl".

Next, try running a simple fio write test to a single file on the Lustre filesystem. Then, assuming you're using >1 OSS, use the following command to configure a new file with [Lustre File Striping](http://wiki.lustre.org/Configuring_Lustre_File_Striping) to distribute the write across as many Object Storage Servers (OSS) as possible with a stripe count of -1. Then rerun the test to see the increased performance!

    lfs setstripe -c -1 /mnt/lustre/testfile_stripe_wide

## Troubleshooting

### Lustre Installation
If the message that the Lustre installation is complete does not appear after 5-10 minutes, and a cluster reboot, please check /var/log/messages to see the messages prefaced by "startup-script:". If there is a bug please submit feedback according to the Feedback section below.

### Lustre Client Mounting
If you receive a "Connection timed out" error while mounting a client check "lctl ping < NODE Hostname / IP >" to ensure that the nodes can communicate over [LNET](http://wiki.lustre.org/Lustre_Networking_(LNET)_Overview). If you receive an Input/Output error please ensure that the firewall rules, routing and VPC networking is configured correctly. 

Refer to the Lustre Wiki page [Mounting a Lustre File System on Client Nodes](http://wiki.lustre.org/Mounting_a_Lustre_File_System_on_Client_Nodes) for more information.

### Lustre Community
The largest source of information for Lustre is the [Lustre wiki](http://lustre.org/), and the [Lustre mailing lists](http://lustre.org/mailing-lists/). If you experience issues with Lustre itself, please refer to those resources first.

## Discussion Group & Feedback
To ask questions or post customizations to the community, please use the [Google Cloud Lustre Discuss Google group](https://groups.google.com/forum/#!forum/google-cloud-lustre-discuss).

To request features, provide feedback, or report bugs please use [this form](https://docs.google.com/forms/d/e/1FAIpQLSfoyL6MneXmUiTV5DFdXeJZ8N9pR3o-GmbFjduKW0DfOOIQdA/viewform?usp=sf_link).

## To Do
- Local SSD support
- Multiple MDS node support
- MDS IP Range support
- Add auth server field
