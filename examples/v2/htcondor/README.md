# HTCondor Cloud Deployment Manager

HTCondor provides a high-throughput job scheduling and management that is
commonly used in the scientific computing space to execute large numbers of
batch jobs on a large number of compute nodes. Users submit jobs to the
scheduler that then matches the job requirements to available compute nodes and
schedules the jobs on appropriate nodes in the pool.

[HTCondor](https://research.cs.wisc.edu/htcondor/) is open source software
developed by Center for High Throughput Computing and Miron Livny at the
University of Wisconsin and is used extensively by the Open Science Grid,
FermiLab and CERN and many other technical computing environments.

These deployment scripts spin up a variable sized HTCondor cluster with a single
condor master, a single condor submit host, and _n_ condor compute nodes.

## To Use

To deploy, you must have a GCP account and have gcloud installed.

1.  edit the `condor-cluster.yaml` file and specify the required values

    For example:

    ```
    resources:
    - name: condor-cluster
      type: condor.jinja
      properties:
        count: 2
        zone: us-central1-f
        email: your.email@provider.com
        instancetype: n1-standard-4
        instanceosfamily: centos
        instanceosversion: 6
        condorversion: 8.4.11-1.el7
    ```

    *   the `count` specifies the number of compute nodes in the cluster provisioned at deployment time
    *   `zone` is the zone and region in which to launch the vms
    *   `email` is used for the configuration of htcondor (optional)
    *   `instancetype` is the type of nodes to use

    Note: the DM scripts use preemptible vms for the compute nodes.

2.  Spin up the cluster.

    Assuming that you have gcloud configured for your account, you can just run:
    `% gcloud deployment-manager deployments create mycondorcluster --config
    condor-cluster.yaml`

3.  Check the cluster status.

    To verify that the deployment scripts all worked, ssh to the submit host and
    run `% condor_status` to see how many cores are registered. Should be n * 4
    (assuming the n1-standard-4 instance type).

    ```
    % gcloud compute ssh condor-submit
    ```

    Then once on the submit host, run

    ```
    % condor_status
    ```

    and check the total number of cores available in the cluster. Output should
    end with:

    ```
                       Total Owner Claimed Unclaimed Matched Preempting Backfill  Drain

          X86_64/LINUX     8     0       0         8       0          0        0      0

                 Total     8     0       0         8       0          0        0      0
    ```

4.  Submit primes jobs into the cluster.

    In the condor-master node, create a file and add the content from
    `applications/primes.c`. Compile this into simple C source program:

    ```
    % gcc -o primes primes.c
    ```

    Create a file called submitprimes (see `applications/submitprimes`):

    ```
    Universe   = vanilla
    Executable = primes
    Arguments  = 400000
    Log        = /var/log/condor/jobs/stats.log
    should_transfer_files = IF_NEEDED
    Queue 100
    ```

    Submit the jobs using the command:

    ```
    % condor_submit submitprimes
    ```

5.  Use GCE console or the condor_history command to see jobs execute and
    complete, i.e.:

    ```
    % condor_history  --userlog /var/log/condor/jobs/stats.log
    ```

6.  Turn off all cluster resources when not in use, i.e.:

    ```
    % gcloud deployment-manager deployments delete mycondorcluster
    ```

## Files

Description of the files in this repo:

-   `README.md` - this file.
-   `condor-cluster.yml` - an example cluster definition file. Edit this to suit
    your needs by supplying parameters.
-   `condor.jinja` and `condor.jinja.schema` - deployment manager type
    definition of type _condor_.
-   `condor-simple.yaml` - a condor cluster defined explicitly without creating
    a type. Used as example only.
-   `applications/primes.c` - sample application to submit into the condor
    cluster for execution.
-   `application/submitprimes` - sample submit

## References

-   Tutorial
-   Google Cloud Solutions
-   Cloud Deployment Manager
-   Google Cloud Platform
-   HTCondor
