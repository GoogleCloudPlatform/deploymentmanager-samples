# HTCondor Compute Cluster Resizing Based  on the Number of Jobs in the Queue

[HTCondor](https://research.cs.wisc.edu/htcondor/) is a framework for 
solving computationally intensive problems.
When HTCondor is installed in the Cloud, it is beneficial to change the 
number of compute instances based on the number of jobs in order to find 
a solution faster. autoscaler.py is a Python script that checks 
number of active jobs in HTCondor queue and  resizes compute cluster in the Cloud to meet the demand.
If this script is setup to run periodically, for example by a cron job, it will 
update number of HTCondor compute instances to be proportional to the number
of jobs waiting in the queue. That will improve the time to completion of 
the jobs.

## Features

This script provisions compute resources for HTCondor proportionally to the 
number of jobs in the queue (running, idle, etc.) In the default 
implementation, the number of compute instances is calculated as directly 
proportional to the total number of jobs in the job queue (e.g. one core per 
job). It is possible to adjust the formula used to calculate the number of 
running nodes for additional optimizations based on the size of jobs and job 
submission pattern. Compute nodes are managed via a GCP managed instance group. 
The size of the cluster is defined by the script by changing the TargetSize of 
the group. Using managed instance groups is convenient to maintain the desired
cluster size also with ephemeral resources, such as preemptible virtual machines.

The script also verifies if compute nodes are idle (no jobs scheduled on the 
HTCondor resource) and shut them down by removing them from the managed instance 
group. In particular, when no jobs are in the queue anymore, the size of the 
cluster will be zero (no compute nodes in the cluster.)

## Getting Started

We assume that an HTCondor cluster is running on GCP prior to installing and configuring the autoscaler script

### Prerequisites

Please follow instructions from https://cloud.google.com/solutions/high-throughput-computing-htcondor 
to set up HTCondor in the GCP environment. Make sure to use attribute `setup_autoscaler = false` in 
the properties of your condor-cluster, since this autoscaler will control the resources.

Other dependencies include Python, the GoogleApiClient and oauth2client 
for Python (installed on the submit node by default).

Note that the default quota on the number of instances (CPUs) may be too low 
as set by default. The current instance quota can be checked on the quota
console page and can be increased by clicking the “Edit Quota” button on 
that page.

Access to the Google Cloud Compute Engine API should be enabled. The HTCondor
submit node has the API enabled as part of its deployment. Please 
follow instructions on https://cloud.google.com/apis/docs/enable-disable-apis 
to enable this API from the management console to enable the API for other nodes.

The script assumes that the Managed Instance Group for the compute nodes is 
provisioned. Make sure that the “Maximum number of instances” parameter is 
as big as the largest cluster that should be provisioned.
 
### Script Arguments

Script accepts the following arguments:
 
| Argument      | Alternative | Description    |
| ------------- | ----------- |-------------- |
| --project_id  | -p | GCP Project ID |
| --region      | -r | GCP region where the managed instance group is located |
| --zone        | -z | Name of GCP zone where the managed instance group is located |
| --group_manager | -g | Name of the managed instance group |
| --verbosity (optional) | -v | Show detail output. 1 - show basic debug info. 2 - show detail debug info |
| --computeinstancelimit (optional) | -v | Maximum number of compute nodes that can be started from the script. Default is no limit enforced by this script |
| -help (optional) | -h | Show command line help information |
 
Example for starting the script:

```
python autoscaler.py --project_id slurm-var-demo --region us-central1 --zone us-central1-f --group_manager condor-compute-igm --verbosity 2
```

### Deployment

1.  Download the autoscaler.py script in a directory on condor-submit node 
2.  Authenticate the user or service account associated with the node to access
    the GCE API. Note that the instanceAdmin role will be sufficient. 
    Alternatively, a new role that includes the ```compute.instanceGroupManagers.*```
    permission set will provide a more granular permission scheme. 

    Refer to 
    https://cloud.google.com/sdk/docs/authorizing and
    https://cloud.google.com/sdk/gcloud/reference/auth/login for more details on 
    account authorization 
    
3.  Update the cron configuration to run the script periodically. For example, 
    to run the script every minute, configure the cron job as following:
    <nobr>
    ```
    * * * * *  /usr/bin/python /<directory_with_script>/autoscaler.py <arguments>
    ```
    </nobr>

### Test

You can test the functionality of the script by running jobs groups with 
different expected execution length. You can use, for example, the application 
provided in the “htcondor on GCP” solution to calculate the first x prime 
numbers. Submit different job groups with various values for x (e.g. 400,000 
and 4,000,000) and observe how the cluster size varies with time as jobs are 
submitted, execute, and finish.
