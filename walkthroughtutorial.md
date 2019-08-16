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

## Viewing the new `two-vms.yaml`

Return to the root directory using the following command:

```sh  
cd -  
```

To open the new `two-vms.yaml` file with the network and references, first use the following command:

```sh  
cd examples/v2/step_by_step_guide/step4_use_references  
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

## Viewing a template

Return to the root directory using the following command:

```sh  
cd -  
```

To open the new `two-vms.yaml` file with the network and references, first use the following command:

```sh  
cd examples/v2/step_by_step_guide/step5_create_a_template/python  
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

In this step, you will explore a template that imports another template. You will examine a template for a network and a template for a firewall rule to allow incoming traffic on port 80.

After this step, your configuration only needs to call a single template to create a deployment with all of these resources.

## Viewing a template for a network

Create a new template file named `network-template.py` with the following network definition:

```py  
"""Creates the network."""

def GenerateConfig(unused_context):  
  """Creates the network."""

  resources = [{  
      'name': 'a-new-network',  
      'type': 'compute.v1.network',  
      'properties': {  
          'routingConfig': {  
              'routingMode': 'REGIONAL'  
          },  
          'autoCreateSubnetworks': True  
      }  
  }]  
  return {'resources': resources}  
```

## Viewing a template for a firewall

Create a template for a new firewall rule that allows TCP traffic from port 80. Call the file `firewall-template.py`:

```py  
"""Creates the firewall."""

def GenerateConfig(unused_context):  
  """Creates the firewall."""

  resources = [{  
      'name': 'a-firewall-rule',  
      'type': 'compute.v1.firewall',  
      'properties': {  
          'network': '$(ref.a-new-network.selfLink)',  
          'sourceRanges': ['0.0.0.0/0'],  
          'allowed': [{  
              'IPProtocol': 'TCP',  
              'ports': [80]  
          }]  
      }  
  }]  
  return {'resources': resources}  
```

## Viewing a template that uses multiple templates

Create a file named `compute-engine-template.py` with the following code: 

```py  
"""Creates the Compute Engine."""

def GenerateConfig(unused_context):  
  """Creates the Compute Engine with network and firewall."""

  resources = [{  
      'name': 'vm-1',  
      'type': 'vm-template.py'  
  }, {  
      'name': 'vm-2',  
      'type': 'vm-template-2.py'  
  }, {  
      'name': 'network-1',  
      'type': 'network-template.py'  
  }, {  
      'name': 'firewall-1',  
      'type': 'firewall-template.py'  
  }]  
  return {'resources': resources}  
```

## Creating a configuration that uses many templates

Now, create a configuration that uses the templates you created. Make a file named `config-with-many-templates.yaml` and add the following content to the configuration:

```yaml  
imports:  
- path: vm-template.py  
- path: vm-template-2.py  
- path: network-template.py  
- path: firewall-template.py  
- path: compute-engine-template.py

resources:  
- name: compute-engine-setup  
  type: compute-engine-template.py  
```

Even though the configuration didn't directly call the other templates, you should import them because the `compute-engine-template.py` file depends on the rest of the templates to be valid.

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

## Setting template properties and using environment variables

Next, you will learn about the benefits of template properties and environment variables. Then, you will view template properties and environment variables in a configuration.

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

## Using template properties and environment variables

You can convert the template you created in the previous step to utilize the benefits of template properties and environment variables.

Open the `vm-template.py` file. Replace the following parts of the file with the appropriate template properties and environment variables: 

Replace `the-first-vm` with:

```py  
context.env['name']  
```

Replace all occurrences of your project ID with:

```py  
context.env['project']  
```

Next, replace the zone. Replace all occurrences of `us-central1-f` with:

```py  
context.properties['zone']  
```

Replace `f1-micro` with:

```py  
context.properties["machineType"]  
```

Replace `$(ref.a-new-network.selfLink)` with:

```py  
'$(ref.' + context.properties['network'] + '.selfLink)'  
```

After these steps, your `vm-template.py` file should look like this:

```py  
"""Creates the virtual machine."""

COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'

def GenerateConfig(context):  
  """Creates the virtual machine with environment variables."""

  resources = [{  
      'name': context.env['name'],  
      'type': 'compute.v1.instance',  
      'properties': {  
          'zone': context.properties['zone'],  
          'machineType': ''.join([COMPUTE_URL_BASE, 'projects/',  
                                  context.env['project'], '/zones/',  
                                  context.properties['zone'], '/machineTypes/',  
                                  context.properties['machineType']]),  
          'disks': [{  
              'deviceName': 'boot',  
              'type': 'PERSISTENT',  
              'boot': True,  
              'autoDelete': True,  
              'initializeParams': {  
                  'sourceImage': ''.join([COMPUTE_URL_BASE, 'projects/',  
                                          'debian-cloud/global/',  
                                          'images/family/debian-9'])  
              }  
          }],  
          'networkInterfaces': [{  
              'network': '$(ref.' + context.properties['network']  
                         + '.selfLink)',  
              'accessConfigs': [{  
                  'name': 'External NAT',  
                  'type': 'ONE_TO_ONE_NAT'  
              }]  
          }]  
      }  
  }]  
  return {'resources': resources}  
```

## Viewing the updated configuration file

Open `two-vms.yaml`. Remove the line importing `vm-template-2.py`. Your configuration should look like this:

```yaml  
imports:  
- path: vm-template.py

resources:  
- name: vm-1  
  type: vm-template.py  
```

Save your changes and redeploy your configuration to confirm the variables work.

```sh  
    gcloud deployment-manager deployments create deployment-with-template-properties --config two-vms.yaml  
```

### Deleting the deployment

Once again, you will want to delete the deployment to avoid charges. Run the following command to delete the deployment:

```sh  
gcloud deployment-manager deployments delete deployment-with-template-properties  
```

### Looking forward: helper scripts

Next, you will learn how to use helper scripts to efficiently perform repeated tasks.

## Creating a helper script

**Helper scripts** are helper files that make your templates more efficient by performing specific functions. Helper scripts can be used to interpret resource metadata, create files, and launch services. 

In this step, you will add a Python helper script that names a virtual machine given a prefix and a suffix.

Create a helper file called `common.py` with the following code:

```py  
"""Generates name of a VM."""

def GenerateMachineName(prefix, suffix):  
  return prefix + "-" + suffix  
```

Open the `vm-template.py` file. Import `common.py` at the top of the file:

```py  
{% import 'common.py' as common %}  
```

In the `resources` section, change the `name` listing to:

```py  
{{ common.GenerateMachineName("myfrontend", "prod") }}  
```

Your `vm-template.py` file should look like this:

```py  
"""Creates the virtual machine."""

{% import 'common.py' as common %}

COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'

def GenerateConfig(context):  
  """Creates the virtual machine with environment variables."""

  resources = [{  
      'name': {{ common.GenerateMachineName("myfrontend", "prod") }},  
      'type': 'compute.v1.instance',  
      'properties': {  
          'zone': context.properties['zone'],  
          'machineType': ''.join([COMPUTE_URL_BASE, 'projects/',  
                                  context.env['project'], '/zones/',  
                                  context.properties['zone'], '/machineTypes/',  
                                  context.properties['machineType']]),  
          'disks': [{  
              'deviceName': 'boot',  
              'type': 'PERSISTENT',  
              'boot': True,  
              'autoDelete': True,  
              'initializeParams': {  
                  'sourceImage': ''.join([COMPUTE_URL_BASE, 'projects/',  
                                          'debian-cloud/global/',  
                                          'images/family/debian-9'])  
              }  
          }],  
          'networkInterfaces': [{  
              'network': '$(ref.' + context.properties['network']  
                         + '.selfLink)',  
              'accessConfigs': [{  
                  'name': 'External NAT',  
                  'type': 'ONE_TO_ONE_NAT'  
              }]  
          }]  
      }  
  }]  
  return {'resources': resources}  
```

Next, edit your configuration file to import the helper script. Open `two-vms.yaml` and change it to the following:

```yaml  
imports:  
- path: common.py  
- path: vm-template.py

resources:  
- name: vm-1  
  type: vm-template.py  
```

## Deploying your configuration

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

In this step, you will update a deployment by adding custom metadata to an existing resource and creating a new virtual machine resource.

## Viewing the updated configuration file

Open `two-vms.yaml`. Add the following metadata to "vm-1" in the `resources:` section:

```yaml  
metadata:  
      items:  
      - key: 'foo'  
        value: 'bar'  
      - key: 'dev'  
        value: 'vm'  
```

Then, add a new resource:

```yaml  
- name: a-new-vm  
  type: compute.v1.instance  
  properties:  
    zone: us-central1-a  
    machineType: machine-type-url  
      - deviceName: boot  
      type: PERSISTENT  
      boot: true  
      autoDelete: false  
      initializeParams:  
        diskName: a-new-vm-disk  
        sourceImage: image-url  
    networkInterfaces:  
    - network: network-url  
```

### Previewing your updated configuration

If you want to preview your updated configuration before committing changes, run the following command:

```sh  
gcloud deployment-manager deployments update deployment-with-helper-script  \  
  --config two-vms.yaml --preview  
```

### Committing the update

```sh  
gcloud deployment-manager deployments update deployment-with-helper-script  
```

### Deleting the deployment

Once again, you will want to delete the deployment to avoid charges. Run the following command to delete the deployment:

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
