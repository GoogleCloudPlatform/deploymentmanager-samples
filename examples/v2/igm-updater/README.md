# Instance Group Updater Example

This example creates two instance groups in two different zones in the same
region. It creates a level 3 load balancer over the two instance groups. Most
importantly, it uses the Instance Group Updater to perform a rolling update of
your instance groups.

This example consists of:

*   4 python templates
    *   ha-service.py - the top level template
        *   Uses service.py for each zone.
        *   Uses lb-l3.py to create the load balancer
    *   service.py
        *   Creates the instance templates, using instance-template.py
        *   Creates the instance group
        *   On update, creates the instance group updater
    *   lb-l3.py
        *   Creates the level 3 load balancer over the two regions
    *   instance-template.py
        *   Creates the instance templates.
*   a schema file for the top level python template
    *   Defines the required inputs and defaults for the optional ones
        properties.
*   3 yaml files - used to test the templates with rolling out different linux
    distros

To perform a rolling update on an instance group, four resources are needed:

1. the instance group
1. the previous instance template (for rollbacks if the update fails)
1. the current (ie new) instance template
1. the instance group updater resource

The update will take several minutes to run, so be patient.

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
