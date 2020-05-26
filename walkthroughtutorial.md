# Explore Deployment Manager 

## Overview

This tutorial is a walkthrough of Deployment Manager best practices. As you complete this guide, you will learn techniques to build complex deployments:

+   Creating a deployment configuration
+   Deploying resources
+   Using templates
+   Using helper scripts

After completing this tutorial, you can apply these techniques to carry out tasks such as:

+   Creating and managing Google Cloud resources using templates
+   Harnessing templates to reuse deployment paradigms
+   Deploying multiple resources at once
+   Configuring Google Cloud resources such as Cloud Storage, Compute Engine, and Cloud SQL to work together

This tutorial assumes that you are familiar with YAML syntax and are comfortable running commands in a Linux terminal. 

### Select a project

Select a Google Cloud project to use for this tutorial.

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

## Understanding configurations

A **configuration** defines the structure of a deployment. You must specify a configuration to create a deployment.

In this step, you will access a configuration that creates a deployment with two instances. An **instance** is one of several kinds of resources you can deploy with Deployment Manager.

## Access a configuration

To access the configuration, first use the following command:

```sh  
cd cloudshell_open/deploymentmanager-samples/examples/v2/step_by_step_guide/step2_create_a_configuration  
```

Next, open the file `two-vms.yaml`:

```sh  
cloudshell edit two-vms.yaml  
```

You will now be able to view your configuration file, which has two resources: `the-first-vm` and `the-second-vm`.  Note that each resource has a `name`, `type`, and `properties` field.

### Update your project ID

Replace all instances of "MY_PROJECT" in the file with your project ID:

```sh  
sed -i -e 's/MY_PROJECT/{{project-id}}/g' two-vms.yaml  
```

### Looking ahead: deploying resources

You can use this configuration file to create a deployment. To learn how to deploy the resources in your configuration, continue to the next step. 

## Deploying your resources

A **deployment** creates a set of resources defined in a configuration. Since a deployment contains the resources defined in the configuration, your deployment in this tutorial will have two virtual machine instances.

## Deploy the configuration

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

## View the deployment

Run the following command to view the deployment. You will see a list of each resource in the deployment, along with the resource type, unique resource ID, resource name, and resource creation status:

```sh  
gcloud deployment-manager deployments describe deployment-with-2-vms  
```

### View deployment resources

You can view a list of resources to quickly see which resource might be causing the issue.

To get a list of deployment resources, run:

```sh  
gcloud deployment-manager resources list --deployment deployment-with-2-vms  
```

## Delete your deployment

You won't use this deployment for the remainder of the tutorial. Since Compute Engine resources incur charges, you should delete this deployment. Deleting a deployment also deletes all the resources in a deployment. 

**If you don't delete the deployment, you will run into conflicts with future examples.**

To delete this deployment:

```sh  
gcloud deployment-manager deployments delete deployment-with-2-vms  
```

### Looking ahead: references

Next, use references to improve troubleshooting and to access properties of other resources in your deployment.

## Understanding the benefits of references

You can use **references** to define the properties of your configuration or templates instead of directly providing values.

With references, you can access properties that are not defined until the resource is created. For example, when you define a virtual machine in your configuration, you do not know its IP address. However, you can create a reference to the IP address.

Next, you will examine an updated `two-vms.yaml` that contains a network, as well as virtual machine instances that reference the network. 

## Exploring the new `two-vms.yaml`

First, run the following command to open your home directory:

```sh  
cd  
```

To open the new `two-vms.yaml` file with the network and references, first use the following command:

```sh  
cd cloudshell_open/deploymentmanager-samples/examples/v2/step_by_step_guide/step4_use_references  
```

Then, open the `two-vms.yaml` file:

```sh  
cloudshell edit two-vms.yaml  
```

### Viewing the reference to a network

In the properties section of both of your virtual machine instances, the value of `network` is replaced with a reference to the new network's `selfLink` property.

## Deploy your new configuration

### Update your project ID

Replace all instances of "MY_PROJECT" in `two-vms.yaml` with your project ID:

```sh  
sed -i -e 's/MY_PROJECT/{{project-id}}/g' two-vms.yaml  
```

### Deploy your configuration

Deploy your configuration with the following command: 

```sh  
gcloud deployment-manager deployments create deployment-with-references --config two-vms.yaml  
```

To view your deployment, use the following command: 

```sh  
gcloud deployment-manager deployments describe deployment-with-references  
```

## Delete Your Deployment

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

First, run the following command to open your home directory:

```sh  
cd  
```

Next, change directories with the following command:

```sh  
cd cloudshell_open/deploymentmanager-samples/examples/v2/step_by_step_guide/step5_create_a_template/python  
```

Then, open the `vm-template.py` file:

```sh  
cloudshell edit vm-template.py  
```

Replace all instances of "MY_PROJECT" in the file with your project ID:

```sh  
sed -i -e 's/MY_PROJECT/{{project-id}}/g' vm-template.py  
```

## Editing a second template

There is a second template in this directory called `vm-template-2.py`. Like `vm-template.py`, `vm-template-2.py` creates a virtual machine. 

To view `vm-template-2.py`, run the following command:

```sh  
cloudshell edit vm-template-2.py  
```  
   
Replace all instances of "MY_PROJECT" in the file with your project ID:

```sh  
sed -i -e 's/MY_PROJECT/{{project-id}}/g' vm-template-2.py  
```

## Importing templates

Open the `two-vms.yaml` file in this directory with the following command:

```sh  
cloudshell edit two-vms.yaml  
```

In this updated file, the templates are imported at the top of the file. The properties of the resources are replaced with the names of the templates. 

## Naming resources

When you use a template, your resource names are defined using the `name` field provided in the template, not the name in the configuration file.

For example, in this case, the virtual machine instances are created using the names in the templates you created, "the-first-vm" and "the-second-vm." The values "vm-1" and "vm-2," defined in the configuration, are used to name an instantiation of the template, but are not resource names, unless you decide to use environment variables to set both names to be the same.

## View the deployment

Save your configuration and deploy it: 

```sh  
 gcloud deployment-manager deployments create deployment-with-templates --config two-vms.yaml  
```

To view your deployment, run the following command:

```sh  
 gcloud deployment-manager deployments describe deployment-with-templates  
```

## Delete the deployment

Once again, you will want to delete the deployment to avoid charges. Run the following command to delete the deployment:

```sh  
gcloud deployment-manager deployments delete deployment-with-templates  
```

### Looking ahead: using multiple templates

Next, combine templates so that your configuration only calls one template to deploy all your resources.

## Using multiple templates

Next, you will explore a template that imports other templates. 

After incorporating these templates, your configuration only needs to call a single template to create a deployment with all of these resources.

## Exploring a template that uses multiple templates

The template in this example creates a Compute Engine with a network and a firewall.

### Access the template

First, use the following command to open your home directory:

```sh  
cd  
```

Next, use the following command:

```sh  
cd cloudshell_open/deploymentmanager-samples/examples/v2/step_by_step_guide/step6_use_multiple_templates/python  
```

To view this template, run the following command:

```sh  
cloudshell edit compute-engine-template.py  
```

### Viewing the template's resources

The template's resources include `vm-template.py`, `vm-template-2.py`, `network-template.py`, and `firewall-template.py`. You can view these templates using the `cloudshell edit {file-name}` command.

## Importing many templates into a configuration 

Now, you will explore a configuration that uses the template you previously viewed. 

To see this file, run the following command:

 ```sh  
cloudshell edit config-with-many-templates.yaml  
```

Notice that the configuration did not directly call the other templates. However, the other templates are imported because `compute-engine-template.py` depends on the other templates to be valid.

## Deploy your configuration

Save your configuration and deploy it:

```sh  
gcloud deployment-manager deployments create deployment-with-many-templates --config config-with-many-templates.yaml  
```

To view your deployment, run the following command:

```sh  
gcloud deployment-manager deployments describe deployment-with-many-templates  
```

## Delete your deployment

Once again, you will want to delete the deployment to avoid charges. Run the following command to delete the deployment:

```sh  
gcloud deployment-manager deployments delete deployment-with-many-templates  
```

### Looking ahead: exploring template potential

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

In this step, `vm-template.py` shows the benefits of template properties and environment variables.

To view the new `vm-template.py`, first use the following command to open your home directory:

```sh  
cd  
```

Next, run the following command:

```sh  
cd cloudshell_open/deploymentmanager-samples/examples/v2/step_by_step_guide/step7_use_environment_variables/python  
```

Then, open the `vm-template.py` file:

```sh  
cloudshell edit vm-template.py  
```

### Exploring the changes

Various parts of the file have been replaced with template properties and environment variables. For example, the project ID is replaced with `context.env[`project`]`. Read the file comments to learn about other changes in the file.

## Deploy your configuration

To view the configuration file for this deployment, run the following command:

```sh  
cloudshell edit config-with-many-templates.yaml  
```

Save your changes and redeploy your configuration to confirm the variables work.

```sh  
    gcloud deployment-manager deployments create deployment-with-template-properties --config config-with-many-templates.yaml  
```

## Delete the deployment

Once again, you will want to delete the deployment to avoid charges. Run the following command to delete the deployment:

```sh  
gcloud deployment-manager deployments delete deployment-with-template-properties  
```

### Looking ahead: helper scripts

Next, you will learn how to use helper scripts to efficiently perform repeated tasks.

## Exploring helper scripts

**Helper scripts** are helper files that make your templates more efficient by performing specific functions. Helper scripts can be used to interpret resource metadata, create files, and launch services. 

You will now explore a Python helper script that names a virtual machine, given a prefix and a suffix.

## Viewing the helper script

The helper script in this example generates the name for a virtual machine. To view the helper script, first run the following command to open your home directory:

```sh  
cd  
```

Next, change to this directory: 

```sh  
cd cloudshell_open/deploymentmanager-samples/examples/v2/step_by_step_guide/create_a_helper_script  
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

### Exploring the changes

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

## View your deployment

View your deployment with the following command:

```sh  
 gcloud deployment-manager deployments describe deployment-with-helper-script  
```

## Delete the deployment

Once again, you will want to delete the deployment to avoid charges. Run the following command to delete the deployment:

```sh  
gcloud deployment-manager deployments delete deployment-with-helper-script  
```

### Looking forward: updating deployments

Next, learn to add, delete, and change the properties of resources of a deployment as your application evolves.

## Updating a deployment

Once you have created a deployment, you can update it as your application changes. You can use Deployment Manager to update a deployment by:

+   Adding or removing resources from a deployment
+   Updating the properties of existing resources in a deployment

You will now update a deployment by changing the metadata in `vm-template.py`.

## Deploy the original configuration

In this step, deploy the configuration that you will later update.

First, run the following command to open your home directory:

```sh  
cd  
```

Next, change to this directory: 

```sh  
cd cloudshell_open/deploymentmanager-samples/examples/v2/step_by_step_guide/step8_metadata_and_startup_scripts/python  
```

Deploy your configuration:

```sh  
gcloud deployment-manager deployments create deployment-to-update --config config-with-many-templates.yaml  
```

## Viewing the updated template

In this example, the metadata is changed in `vm-template.py`.

To view these changes, first run the following command to open your home directory:

```sh  
cd  
```

Next, change to this directory: 

```sh  
cd cloudshell_open/deploymentmanager-samples/examples/v2/step_by_step_guide/step9_update_a_deployment/python  
```

Then, open `vm-template.py`:

```sh  
cloudshell edit vm-template.py  
```

Notice that the metadata section is changed in the file. 

## Commit the update

### Preview the configuration

To preview your updated configuration before committing changes, run the following command:

```sh  
gcloud deployment-manager deployments update deployment-to-update --config config-with-many-templates.yaml --preview  
```

### Update the configuration

To commit the update, run the following command:

```sh  
gcloud deployment-manager deployments update deployment-to-update  
```

## Delete the deployment

You will want to delete the deployment to avoid charges. Run the following command to delete the deployment:

```sh  
gcloud deployment-manager deployments delete deployment-to-update  
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

+   [Explore more complex tutorials](https://cloud.google.com/deployment-manager/docs/tutorials)
+   Page on metadata and startup scripts
+   [Learn about available resource types](https://cloud.google.com/deployment-manager/docs/configuration/supported-resource-types) 
+   [Read the environment variables documentation](https://cloud.google.com/deployment-manager/docs/configuration/templates/use-environment-variables)
+   [Read about importing Python libraries](https://cloud.google.com/deployment-manager/docs/configuration/templates/import-python-libraries)
+   [Understand guidelines for preparing updates](https://cloud.google.com/deployment-manager/docs/deployments/updating-deployments) 
