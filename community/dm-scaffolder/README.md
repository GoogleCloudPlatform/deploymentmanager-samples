# Deployment Manager Scaffolder
Generate Deployment Manager configs from existing resources

***

## Disclaimer

This tool is an answer to a common GCP customer request: importing existing resources to Deployment Manager. 

> This tool is a SCAFFOLDING tool. The output configurations are **NOT** meant to be launched directly. 
The output is not a 100% representation of your current environment, manul review is highly recommended.

***

## Overview

Many projects start with a quick&dirty, manual implementation before transition to a more structured, 
**Infrastructure as Code** based development. At this point there is the common wish: Lets keep what we have 
and "import" it into Deployment Manager!

This code is intended to help during this transition.
Running the tool gives you close to ready Deployment Manager configurations referencing 
[base types](https://cloud.google.com/deployment-manager/docs/configuration/supported-gcp-types) or 
[Cloud Foundation Toolkit templates (CFT)](https://github.com/GoogleCloudPlatform/deploymentmanager-samples/blob/master/community/cloud-foundation/templates).
> Keep in mind, this is a dump of your current environment. It does NOT follow most of the 
[best practices](https://cloud.google.com/deployment-manager/docs/best-practices/). It is highly recommended 
to [restructure your codebase](https://cloud.google.com/deployment-manager/docs/at-scale), create your own 
wrapper templates and remove duplicates from your configuration files.

## Why should I use it?

Using this tool saves you a large amount of time during the initial steps of your Infrastructure as Code 
transition. If you use the CFT templates, you are getting a large set of high quality templates, which 
sets a great baseline in code quality and best practices.

## What about Forseti?

During this initial version the DM Scaffolder is using gcloud calls to get the inventory of your resources. 
This is a simpler implementation of the same feature as Forseti is doing. Potentially in the future there will 
be tighter integration with Forseti.

## How do I use it?

1. Copy the **configs.yaml.example** to **config.yaml**
2. Fill out the **configs.yam**l file with the mandatory configuration values like your **Organization ID**.
3. Make sure that **gcloud** is installed and authenticated.
  1. Make sure the authenticated user or service account has the appropriate rights for listing the resources 
  you are interested in.
4. Edit the **scaffolder.py** file to define which resources are you interested.
5. Run `python scaffold.py` (Optionally pipe the output to a file.)

The generated configuration files are almost ready to launch, but it's highly suggested to apply the following changes:
- Decide your deployment hierarchy
  - Choose a central project for project creation
    - Create each project in a separate deployment in the central project
  - Split up the rest of your resources into deployments
    - Choose a project for each deployment
    - Make sure all resources are in a deployment in a matching project
  - Remove hard coded IDs from your configuration files
    - Add Cross deployment references if you are using the [CFT cli](https://github.com/GoogleCloudPlatform/deploymentmanager-samples/blob/master/community/cloud-foundation/templates)

## What should I avoid?

- Do NOT believe the output of this scaffolder is `Infrastructure as Code(IaC)` by any standards.
- Do NOT believe IaC is not `code`. All general coding practices apply:
  - Structure your codebase
    - Separate configuration from Code
    - Do not Repeat Yourself [DRY](http://wikipedia.com/dry) ( Neither code nor configuration.) 
    - Structure your configurations into local, global, environment specific, etc configuration files.
    - Split your resources into multiple deployments
    - Use references within and between* deployments (*with the help of the CFT cli or custom implementation)
  - Reuse community templates
    - Only use high quality templates like the CFT implementation
  - Write your own (wrapper) template where you require additional functionality.
    - Define and document your templates schema
    - Enable your teams to reuse your high quality templates
    - Contribute to community templates
  - Think about pipelines and not individual deployments
- Avoid doing manual changes in your system. The scaffolding is a one-off step at the beginning in your IaC journey.

## Different versions, I'm confused!

The GCP product teams are constantly improving their products feature set. This means new versions of 
APIs are constantly popping up. Some of these versions are still in Alpha or Beta, sometimes there is 
a trade off to use the Generally Available(GA) V1 API or the V2Beta which may has additional features.

The scaffolder does not care about the versions, it puts all the output of the gcloud query into the 
output configurations. However setting the appropriate API version makes your output compatible with 
that version when you launch the deployment.

### The `CFT` version

The Cloud Foundation Toolkit works in many cases similar to an API version. It has some times 
different inputs, some property aggregation may be needed but the output will be Deployment Manager 
configuration files. The difference is the resource types. Instead of calling `gcp-types` directly, 
the configuration is referencing Deployment Manager templates part of the CFT library.

Many of these templates are providing a simplified interface, additional features and well 
documented schemas and examples for your team. Highly encouraged to use these templates.

## Providers

The DM Scaffolder tool is designed in a modular way for easy extensibility.
Currently the following GCP resources are supported:
- Folders
- Projects
  - Shared VPC (if you use the CFT version)
- Networks (VPC)
  - Subnetworks
- Firewalls (per project)
- PubSub (per project)
  - Topics
  - Subscriptions per topics

## Feedback and contribution

As of early 2019 this tool is in early stage. Please send us feedback via Github issues, 
we are closely monitoring that channel.

If you have any improvement ideas, you are more then welcome to send a Pull Request which 
will be reviewed and likely included to the solution.

## Example usage

scaffolder.py:
```
from dm_config import DMConfig
from providers.firewall import FirewallCFT
from providers.folder   import FolderCFT
from providers.project  import ProjectCFT
from providers.network  import NetworkCFT
from providers.pubsub   import PubSubTopicCFT

#DMConfig(FolderCFT().get_list())
#DMConfig(ProjectCFT().get_list())
#DMConfig(NetworkCFT().get_list())
DMConfig(FirewallCFT().get_list("--project=cft-test-workspace-221111"))
#DMConfig(PubSubTopicCFT().get_list("--project=cft-test-workspace-221111"))
```

Execution:
```
# Create output directory if needed
# mkdir sample_output
python scaffolder.py > sample_output/cft_folder.yaml
python scaffolder.py > sample_output/cft_project.yaml
python scaffolder.py > sample_output/cft_network.yaml
python scaffolder.py > sample_output/cft_firewall_1.yaml
python scaffolder.py > sample_output/cft_pubsub_1.yaml
```
(Note: For each run, you need to change the scaffolder.py according which resource you wish to dump or you need to handle the output from the scaffolder.py.)


Example output:

Folder:
```
imports:
- path: ../templates/folder/folder.py
resources:
- type: ../templates/folder/folder.py
  name: not_set
  properties:
    folders:
    - displayName: admin
      name: folders/235200341656
      parent: organizations/518838582041
- type: ../templates/folder/folder.py
  name: not_set
  properties:
    folders:
    - displayName: Shared Infrastucture
      name: folders/992727879184
      parent: organizations/518838582041
```

Project:
```
imports:
- path: ../templates/project/project.py

- type: ../templates/project/project.py
  name: kaz-sandbox
  properties:
    name: kaz-sandbox
    parent:
      id: '518838582041'
      type: organization
    projectId: kaz-sandbox
    projectNumber: '731003428239'
    removeDefaultVPC: true
    removeDefaultSA: true
    billingAccountId: billingAccounts/01C7EB-1BF720-2870E7

```