# Deployment Manager Quickstart

To restart this tutorial, run this command in the Cloud Shell terminal:

```sh
teachme ~/cloudshell_open/deploymentmanager-samples/quickstart.md
```

## Introduction

In this quickstart, you use Deployment Manager to deploy a virtual machine
instance. The virtual machine is a *resource*, which you add to a deployment
*configuration* file. After you create a configuration file, you use it to
create a *deployment*, which is a collection of resources that you can create
or manage together.

Your deployments can contain dozens of resources from various Google Cloud
services, and you use Deployment Manager to manage them from a single
file.

This quickstart walks you through creating a basic configuration file, and using
that file to create a deployment. To complete this tutorial, you must be
comfortable running commands in a Linux terminal.


## Setting up

1. Select or create a Google Cloud Platform project:

    <walkthrough-project-setup></walkthrough-project-setup>

1. [Enable billing](https://support.google.com/cloud/answer/6293499#enable-billing).

1. Configure the `gcloud` command-line tool to use your project:

    ```sh
	gcloud config set project {{project-id}}
    ```

1. Run this command to enable the Deployment Manager and Compute APIs:

    ```sh
    gcloud services enable compute.googleapis.com deploymentmanager.googleapis.com  
    ```

## Define your resources

To begin, run these commands to open the quickstart configuration in `vm.yaml`:

```sh
cd ~/cloudshell_open/deploymentmanager-samples/examples/v2/quick_start/
cloudshell edit vm.yaml
```

This basic configuration file describes a deployment that contains one
virtual machine instance with the following properties:

+ Machine type: `f1-micro`
+ Image family: `debian-9`
+ Zone: `us-central1-f`
+ Root persistent disk: `boot`
+ A randomly assigned external IP address

In the configuration file, replace `[MY_PROJECT]` with your project ID.
 
To save your changes, from the **File** menu, click **Save**.

## Deploy the resources

To deploy your resources, use the `gcloud` command-line tool to create a new
deployment, using your configuration file:

```sh
gcloud deployment-manager deployments create quickstart-deployment --config vm.yaml
```

## Check on your deployment

To check the status of the deployment, run this command:

```sh
gcloud deployment-manager deployments describe quickstart-deployment
```

## Review your resources

After you have created the deployment, you can review your resources in the
Cloud console.

1. To see a list of your deployments,
    [open the Deployment Manager page](https://console.cloud.google.com/dm/deployments).

1. To see the resources in the deployment, click **quickstart-deployment**. The
   deployment overview opens, with information about the deployment, and the
   resources that are part of the deployment.

1. To see information about your VM, click **quickstart-deployment-vm**.

## Clean up

To avoid incurring charges on your Cloud Platform account, delete the deployment and
all the resources that you created:

```sh
gcloud deployment-manager deployments delete quickstart-deployment
```

## What's next

* Work through the [Step-by-Step Guide to Deployment Manager](https://cloud.google.com//deployment-manager/docs/step-by-step-guide/).
* Read more about [Deployment Manager Configurations](https://cloud.google.com/deployment-manager/docs/configuration/).
* For a list of resources you can create and manage in your deployment, see [Supported
resource types](https://cloud.google.com/deployment-manager/docs/configuration/supported-resource-types).
