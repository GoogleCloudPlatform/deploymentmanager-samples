# Instance Group Updater Example

This example creates two instance groups in two different zones in the same
region. It creates a level 3 load balancer over the two instance groups. Most
importantly, it uses the Instance Group Manager to perform a rolling update of
your instance groups. For more details, check [Updating Managed Instance
Groups](https://cloud.google.com/compute/docs/instance-groups/updating-managed-instance-groups)

This example provides both python templates and jinja templates. For python
templates, this example consists of:

*   4 python templates
    *   ha-service.py - the top level template
        *   Uses service.py for each zone
        *   Uses lb-l3.py to create the load balancer
    *   service.py
        *   Creates the instance templates, using instance-template.py
        *   Creates the instance group
        *   On update, update the instance group
    *   lb-l3.py
        *   Creates the level 3 load balancer over the two regions
    *   instance-template.py
        *   Creates the instance templates
*   a schema file for the top level python template
    *   Defines the required inputs and defaults for the optional ones
        properties.
*   3 yaml files - used to test the templates with rolling out different linux
    distros

To perform a rolling update on an instance group, below resources are needed:

1.  the instance group
1.  the current (ie new) instance template

The update will take several minutes to run, so be patient. Running below
command to monitor the rolling updates of the instances:

```
$ gcloud compute instance-groups managed list-instances <INSTANCE_GROUP_NAME> --zone=<ZONE>
```

The directory also contains three yaml files.
To run the example use them in order.

1.  Create the deployment and deploy the debian image `gcloud deployment-manager
    deployments create MYDEPLOYMENTNAME --config frontendver1.yaml`
1.  Update the deployment with ubuntu `gcloud deployment-manager deployments
    update MYDEPLOYMENTNAME --config frontendver2.yaml`
1.  Update just the first zone with centos `gcloud deployment-manager
    deployments update MYDEPLOYMENTNAME --config frontendver3.yaml`

Although we are using stock OS images, the example is meant to show how images
baked with your own code can be deployed and updated with Deployment Manager.
