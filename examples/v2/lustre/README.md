# Deployment Managed Lustre

This is a Deployment Manager script to deploy a Lustre parallel file system cluster on Google Cloud Platform. This tool deploys the open source Lustre RPMs available on whamcloud.com.

This script deploys MDS/MGS combined node(s), and N OSS nodes. On both node types the IP addresses, machine type, disk type, and disk size are all configurable in the lustre.yaml file.

Please note: This software is provided as-is, with no guarantees of support. This is an example script, and should be used as such.

## Configuration

These scripts are configured using the lustre.yaml configuration file. This file has the following fields:

    ### Configuration Field  : < description;                   valid example;  optional? >
    cluster_name            : < cluster name;                   lustre >
    zone                    : < GCP zone;                       us-central1-a >
    region                  : < GCP region;                     us-central1 >
    cidr                    : < GCP VPC subnet;                 10.20.0.0/16 >
    external_ips            : < boolean;                        True >

    ### Filesystem Configuration
    fs_name                 : < Lustre filesystem name;         lustre;         OPTIONAL >
    lustre_version          : < Lustre version;                 latest-release; OPTIONAL >
    e2fs_version            : < E2FSPROGS version;              latest;         OPTIONAL >

    ### MDS/MGS Configuration
    mds_node_count          : < Num Lustre MDS instances;       1;              OPTIONAL >
    mds_ip_address          : < MDS IP Address range start;     10.20.0.2;      OPTIONAL >
    mds_machine_type        : < MDS instance profile;           n1-standard-16; OPTIONAL >
    mds_disk_type           : < MDS Boot Disk Type;             pd-standard;    OPTIONAL >
    mds_disk_size_gb        : < MDS Boot Disk Size;             40;             OPTIONAL >
    mdt_disk_type           : < Metadata Target Disk Type;      pd-ssd >
    mdt_disk_size_gb        : < MDT Disk Size;                  500 >

    ### OSS Configuration
    oss_node_count          : < Num Lustre OSS instances;       4 >
    oss_ip_range_start      : < OSS IP Address range start;     10.20.0.5;      OPTIONAL >
    oss_machine_type        : < OSS instance profile;           n1-standard-16; OPTIONAL >
    oss_disk_type           : < OSS Boot Disk Type;             pd-standard;    OPTIONAL >
    oss_disk_size_gb        : < OSS Boot Disk size;             100;            OPTIONAL >
    ost_disk_type           : < OST Disk Type;                  pd-ssd >
    ost_disk_size_gb        : < OST Disk Size;                  100 >

## Launch the Lustre Cluster

Once you've customized the lustre.yaml file and completed all the required fields, and ensured you have adequate [resource quota](https://cloud.google.com/compute/quotas), you are ready to launch your Lustre cluster.

Use the following command to launch your Lustre cluster.

$ gcloud deployment-manager deployments create lustre --config lustre.yaml

Once the cluster is deployed, ssh in to the MDS instance. You may notice a message indicating that the Lustre filesystem is still being installed, and that you will be notified when the process is complete. Please wait until you see a second message reporting the installation complete, and providing the sample mount command for your cluster.

## Mount the Lustre filesystem

Once the nodes are installed and the filesystem is online you're ready to mount your clients. Install the [Lustre client software](http://wiki.lustre.org/Installing_the_Lustre_Software#Lustre_Client_Software_Installation) on an instance that is routable to the Lustre cluster's subnet. Once installed, and with the Lustre module loaded, use the following mount command to mount your filesystem:

$ mount -t lustre < MDS #1 Hostname >:< MDS #N Hostname >:/< FS NAME > < LOCAL MOUNT >

An example would be:

$ mount -t lustre lustre-mds1:/lustre /mnt/lustre

You may use the Lustre Metadata Server (MDS) to test if the clients can mount the filesystem. However, please do not leave the filesystem mounted on the MDS server as it may cause filesystem corruption.

Once the filesystem is mounted you will see no output returned with the mount command. You can verify the filesystem is mounted by checking the "mount" command, and by running "lctl dl".

Next, try running a simple fio write test to a single file on the Lustre filesystem. Then, assuming you're using >1 OSS, use the following command to configure a new file with [Lustre File Striping](http://wiki.lustre.org/Configuring_Lustre_File_Striping) to distribute the write across as many Object Storage Servers (OSS) as possible with a stripe count of -1. Then rerun the test to see the increased performance!

$ lfs setstripe -c -1 /mnt/lustre/testfile_stripe_wide

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
- Remove region field
- Add auth server field
