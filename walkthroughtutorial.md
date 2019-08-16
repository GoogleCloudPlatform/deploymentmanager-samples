# Explore Deployment Manager 

## Overview

This tutorial is a walkthrough of Deployment Manager best practices. As you complete this guide, you will learn techniques to build complex deployments:

+   Creating a deployment configuration
+   Deploying resources
+   Using templates
+   Using helper scripts

After completing this tutorial, you can apply these techniques to carry out tasks such as:

+   Creating and managing Google Cloud Platform (GCP) resources using templates
+   Harnessing templates to reuse deployment paradigms
+   Deploying multiple resources at once
+   Configuring GCP resources such as Cloud Storage, Compute Engine, and Cloud SQL to work together

This tutorial assumes that you are familiar with YAML syntax and are comfortable running commands in a Linux terminal. 

Select a GCP Console project to use for this tutorial. 

<walkthrough-project-setup></walkthrough-project-setup>

## Setup

Every command requires a project ID. Set a default project ID so you do not need to provide it every time. 

```sh  
gcloud config set project {{project-id}}  
```

Enable the Compute Engine and Deployment Manager APIs, which you will need for this tutorial.

```sh  
gcloud services enable compute.googleapis.com deploymentmanager.googleapis.com  
```

## Understanding Configurations

A **configuration** defines the structure of a deployment. You must specify a configuration to create a deployment.

In this step, you will access a configuration that creates a deployment with two instances. 

To access the configuration, first use the following command:

```sh  
cd examples/v2/step_by_step_guide/step2_create_a_configuration  
```

Next, open the file `two-vms.yaml`:

```sh  
cloudshell edit two-vms.yaml  
```

You will now be able to view your configuration file, which has two resources: `the-first-vm` and `the-second-vm`.  Note that each resource has a `name`, `type`, and `properties` field.

You can use this configuration file to create a deployment. To learn how to deploy the resources in your configuration, continue to the next step. 

## Deploying your resources

A **deployment** creates a set of resources defined in a configuration. Since a deployment contains the resources defined in the configuration, your deployment in this tutorial will have two virtual machine instances.

Run this command to deploy your configuration:

```sh  
gcloud deployment-manager deployments create deployment-with-2-vms --config two-vms.yaml  
```

Wait for the indication that you successfully created the deployment (note that your actual operation IDs will differ):

```  
Waiting for create operation-1432319707382-516afeb5d00f1-b864f0e7-b7103978...done.  
Create operation operation-1432319707382-516afeb5d00f1-b864f0e7-b7103978 completed successfully.  
NAME           TYPE                 STATE      ERRORS  INTENT  
the-first-vm   compute.v1.instance  COMPLETED  []  
the-second-vm  compute.v1.instance  COMPLETED  []  
```

Run the following command to view the deployment. You will see a list of each resource in the deployment, along with the resource type, unique resource ID, resource name, and resource creation status:

```sh  
gcloud deployment-manager deployments describe deployment-with-2-vms  
```

## Viewing resources of a deployment

You can view a list of resources to quickly see which resource might be causing the issue.

To get a list of deployment resources, run:

```sh  
gcloud deployment-manager resources list --deployment deployment-with-2-vms  
```

### Deleting your deployment

You won't use this deployment for the remainder of the tutorial. Since Compute Engine resources incur charges, you should delete this deployment. Deleting a deployment also deletes all the resources in a deployment. 

**If you don't delete the deployment, you will run into conflicts with future examples.**

To delete this deployment:

```sh  
gcloud deployment-manager deployments delete deployment-with-2-vms  
```

### Looking ahead: references

Next, use references to improve troubleshooting and to access properties that are undefined until a resource is created.

## Understanding reference benefits

You can use **references** to define the properties of your configuration or templates instead of directly providing values.

With references, you can access properties that are not defined until the resource is created. For example, when you define a virtual machine in your configuration, you do not know its IP address. However, you can create a reference to the IP address.

Next, you will examine an updated `two-vms.yaml` that contains a network, as well as virtual machine instances that reference the network. 

## Exploring the new `two-vms.yaml`

First, run the following command:

```sh  
cd  
```

To open the new `two-vms.yaml` file with the network and references, first use the following command:

```sh  
cd deploymentmanager-samples/examples/v2/step_by_step_guide/step4_use_references  
```

Then, open the `two-vms.yaml` file:

```sh  
cloudshell edit two-vms.yaml  
```

You can see that in the properties section of both of your virtual machine instances, the value of `network` is replaced with a reference to the new network's `selfLink` property.

## Deploying your new configuration

Deploy your configuration with the following command: 

```sh  
gcloud deployment-manager deployments create deployment-with-references --config two-vms.yaml  
```

If you would like to view your deployment, you can use the following command: 

```sh  
gcloud deployment-manager deployments describe deployment-with-references  
```

### Deleting Your Deployment

Once again, you will want to delete the deployment to avoid charges. Run the following command to delete the deployment:

```sh  
gcloud deployment-manager deployments delete deployment-with-references  
```

### Looking ahead

To maximize efficiency while building large configurations, follow best practices such as using variables and templates. 

In the next step, you will learn about templates and how they enable flexible, dynamic configurations. 

## Exploring the power of templates

While developing an application, you will most likely require complex architectures. Therefore, we recommend that you break your configuration into templates. 

A **template** is a separate file that defines a set of resources. You can reuse templates across different deployments, which creates consistency across complex deployments.

You can use Python or Jinja2 to create templates for Deployment Manager. We recommend that you use Python templates, because Python allows for greater flexibility and more features as you scale your application. 

Your next task is to create a Python template using the contents of the configuration you created earlier in this tutorial. 

## Examining a template

First, run the following command:

```sh  
cd  
```

Next, change directories with the following command:

```sh  
cd deploymentmanager-samples/examples/v2/step_by_step_guide/step5_create_a_template/python  
```

Then, open the `vm-template.py` file:

```sh  
cloudshell edit vm-template.py  
```

There is a second template in this directory called `vm-template-2.py`. Like `vm-template.py`, `vm-template-2.py` creates a virtual machine. If you would like to view `vm-template-2.py`, run the following command:

```sh  
cloudshell edit vm-template-2.py  
``` 

## Importing templates

Open the `two-vms.yaml` file in this directory with the following command:

```sh  
cloudshell edit two-vms.yaml  
```

In this updated file, the templates are imported at the top of the file. The properties of the resources are replaced with the names of the templates. 

### Naming resources

When you use a template, your resource names are defined using the `name` field provided in the template, not the name in the configuration file.

For example, in this case, the virtual machine instances are created using the names in the templates you created, "the-first-vm" and "the-second-vm." The values "vm-1" and "vm-2," defined in the configuration, are used to name an instantiation of the template, but are not resource names, unless you decide to use environment variables to set both names to be the same.

## Viewing the deployment

Save your configuration and deploy it: 

```sh  
 gcloud deployment-manager deployments create deployment-with-templates --config two-vms.yaml  
```

To view your deployment, run the following command:

```sh  
 gcloud deployment-manager deployments describe deployment-with-templates  
```

### Deleting the deployment

Once again, you will want to delete the deployment to avoid charges. Run the following command to delete the deployment:

```sh  
gcloud deployment-manager deployments delete deployment-with-templates  
```

### Looking ahead: using multiple templates

Next, combine templates so that your configuration only calls one template to deploy all your resources.

## Using multiple templates

Next, you will explore a template that imports another template. You will examine a template for a network and a template for a firewall rule to allow incoming traffic on port 80.

After incorporating these templates, your configuration only needs to call a single template to create a deployment with all of these resources.

## Viewing a template for a network

First, use the following command:

```sh  
cd  
```

To view the network template, use the following command:

```sh  
cd deploymentmanager-samples/examples/v2/step_by_step_guide/step6_use_multiple_templates/python  
```

Then, open the `network-template.py` file:

```sh  
cloudshell edit network-template.py  
```

## Viewing a template for a firewall

The firewall template in this example allows TCP traffic from port 80.

To view the `firewall-template.py` file, run the following command:

```sh  
cloudshell edit firewall-template.py  
```

## Exploring a template that uses multiple templates

The template in the following example creates the Compute Engine with the network and firewall from the previous templates. 

Its resources include `vm-template.py`, `vm-template-2.py`, `network-template.py`, and `firewall-template.py`. 

To view this template, run the following command:

```sh  
cloudshell edit compute-engine-template.py  
```

## Importing many templates into a configuration 

Now, you will explore a configuration that uses all the templates you previously viewed. 

To see this file, run the following command:

 ```sh  
cloudshell edit config-with-many-templates.yaml  
```

Notice that the configuration did not directly call the other templates. However, the other templates are imported because `compute-engine-template.py` depends on the other templates to be valid.

## Deploying your configuration

Save your configuration and deploy it:

```sh  
gcloud deployment-manager deployments create deployment-with-many-templates \  
 --config config-with-many-templates.yaml  
```

To view your deployment, run the following command:

```sh  
gcloud deployment-manager deployments describe deployment-with-many-templates  
```

### Deleting Your Deployment

Once again, you will want to delete the deployment to avoid charges. Run the following command to delete the deployment:

```sh  
gcloud deployment-manager deployments delete deployment-with-many-templates  
```

### Looking forward: exploring template potential

Next, you will learn how to maximize template features such as custom properties to benefit your application development. 

## Learning about template properties

An advantage of using templates is the ability to create and define custom properties, which enable the reuse of templates across zones, regions, and projects.

Template properties are arbitrary variables. Any configuration file or template file can provide a value for a template property without modifying the template. Therefore, you can change a property's value for various configurations without changing the template itself.

To reference an arbitrary value, use this syntax in a template:

```sh  
    context.properties["property-name"]  
```

## Learning about environment variables

Environment variables are predefined variables that populate particular pieces of information from your deployment. Use environment variables in templates to get unique information about your deployment. 

Reference an environment variable using this syntax: 

```sh  
    context.env['variable-name']  
```

## Using template properties and environment variables in a template

In this step, `vm-template.py` is converted to utilize the benefits of template properties and environment variables.

To view the new `vm-template.py`, first use the following command:

```sh  
cd  
```

Next, run the following command:

```sh  
cd deploymentmanager-samples/examples/v2/step_by_step_guide/step7_use_environment_variables/python  
```

Then, open the `vm-template.py` file:

```sh  
cloudshell edit vm-template.py  
```

Various parts of the file have been replaced with template properties and environment variables. For example, `the-first-vm` has been replaced with `context.env['name']`. Read the file comments to learn about other changes in the file.

## Deploying your configuration

If you would like to view the configuration file for this deployment, run the following command:

```sh  
cloudshell edit vm-config.yaml  
```

Save your changes and redeploy your configuration to confirm the variables work.

```sh  
    gcloud deployment-manager deployments create deployment-with-template-properties --config vm-config.yaml  
```

### Deleting the deployment

Once again, you will want to delete the deployment to avoid charges. Run the following command to delete the deployment:

```sh  
gcloud deployment-manager deployments delete deployment-with-template-properties  
```

### Looking forward: helper scripts

Next, you will learn how to use helper scripts to efficiently perform repeated tasks.

## Exploring helper scripts

**Helper scripts** are helper files that make your templates more efficient by performing specific functions. Helper scripts can be used to interpret resource metadata, create files, and launch services. 

You will now explore a Python helper script that names a virtual machine, given a prefix and a suffix.

## Viewing the helper script

The helper script in this example generates the name for a virtual machine. To view the helper script, first run the following command:

```sh  
cd  
```

Next, change to this directory: 

```sh  
cd deploymentmanager-samples/examples/v2/step_by_step_guide/create_a_helper_script  
```

Then, open `common.py`:

```sh  
cloudshell edit common.py  
```

## Using helper scripts in templates

To use `common.py` in `vm-template.py`, several changes must be made to the template.

To view the changes, open the `vm-template.py` file:

```sh  
cloudshell edit vm-template.py  
```

The template contains code comments highlighting the changes made. 

Notice that `common.py` is imported at the top of the file. Also, the `name` listing in the `resources` section is changed to use the script.

## Changing your configuration

The configuration must also be changed to import the helper script. To view this change, open `two-vms.yaml`:

```sh  
cloudshell edit two-vms.yaml  
```

Deploy your configuration to confirm the changes work:

```sh  
gcloud deployment-manager deployments create deployment-with-helper-script --config two-vms.yaml  
```

View your deployment with the following command:

```sh  
 gcloud deployment-manager deployments describe deployment-with-helper-script  
```

**Note that you do not need to delete this deployment yet because you will use it in the next step.**

### Looking forward: updating deployments

Next, learn to add, delete, and change the properties of resources of a deployment as your application evolves.

## Updating the deployment

Once you have created a deployment, you can update it as your application changes. You can use Deployment Manager to update a deployment by:

+   Adding or removing resources from a deployment
+   Updating the properties of existing resources in a deployment

You will now update a deployment by adding custom metadata to an existing resource and creating a new virtual machine resource.

## Viewing the updated configuration file

In this example, a new resource is also added to the configuration file `two-vms.yaml`.

To view these changes, first run the following command:

```sh  
cd  
```

Next, change to this directory: 

```sh  
cd deploymentmanager-samples/examples/v2/step_by_step_guide/step9_update_a_deployment/python  
```

Then, open `two-vms.yaml`:

```sh  
cloudshell edit two-vms.yaml  
```

## Committing the update

### Previewing the configuration

If you want to preview your updated configuration before committing changes, run the following command:

```sh  
gcloud deployment-manager deployments update deployment-with-helper-script  \  
  --config two-vms.yaml --preview  
```

### Updating the configuration

To commit the update, run the following command:

```sh  
gcloud deployment-manager deployments update deployment-with-helper-script  
```

### Deleting the deployment

You will want to delete the deployment to avoid charges. Run the following command to delete the deployment:

```sh  
gcloud deployment-manager deployments delete deployment-with-helper-script  
```

### Next: Wrapping up

## Wrapping up

<walkthrough-conclusion-trophy/>

Congratulations! You've completed the Step-by-Step Walkthrough of Deployment Manager!

You learned skills such as:

+   Deploying resources
+   Creating templates
+   Setting template properties
+   Setting environment variables
+   Creating helper scripts
+   Updating deployments

### What's Next

Here are some areas to explore as you learn more details about specific Deployment Manager functions:

+   Page on metadata and startup scripts
+   [Learn about available resource types](https://cloud.google.com/deployment-manager/docs/configuration/supported-resource-types) 
+   [Read the environment variables documentation](https://cloud.google.com/deployment-manager/docs/configuration/templates/use-environment-variables)
+   [Learn about Compute Engine startup scripts](https://cloud.google.com/compute/docs/startupscript)
+   [Read about importing Python libraries](https://cloud.google.com/deployment-manager/docs/configuration/templates/import-python-libraries)
+   [Understand guidelines for preparing updates](https://cloud.google.com/deployment-manager/docs/deployments/updating-deployments)
+   [Explore more complex tutorials](https://cloud.google.com/deployment-manager/docs/tutorials) 
