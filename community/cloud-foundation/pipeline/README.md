# CFT Sample Pipeline

<!-- TOC -->

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Pipelines](#pipelines)

<!-- /TOC -->

## Overview

You can use the Cloud Foundation toolkit (henceforth, CFT) as a standalone
solution, via its command line interface (CLI) – see
[CFT User Guide](../docs/userguide.md) for details. Alternatively, you can initiate
CFT actions via its API, from a variety of existing orchestration tools, or
from your own application.

This document describes one of the CFT integration scenarios, wherein
you initiate the CFT actions from Jenkins. This Guide uses as an example a
Jenkins-based "sample pipeline" that is included in this CFT directory.

`Note:` This document assumes the reader knows the basics of
[Jenkins](https://jenkins.io/) and the
[Pipeline Plugin](https://jenkins.io/doc/book/pipeline/).

`Note:` The Jenkins-based process is for demonstration purposes only. It is not
intended as a product. Your Jenkins setup is likely to be different for the one
we use/demonstrate; therefore, to achieve similar results, you will need to
modify all the demo files.

## Prerequisites

1. A working Jenkins server.
    - Since different organizations have vastly differently
     Jenkins setups, it isn't the objective of this document to document this
     step. One could use an Compute Image from the
     [Marketplace](https://console.cloud.google.com/marketplace/browse?q=jenkins)
    - Extra Plugins:
        - Pipeline Utility Steps
2. GCP Service Accounts (SA)
    - `Service Account for Jenkins`: Jenkins must be configured with permissions
      necessary to manage DM deployments. This can be done by associating a SA
      to the GCP Compute Instance running Jenkins (if Jenkins is in GCP). Or by
      configuring the SA credentials with the Jenkins user if running Jenkins
      outside GCP
    - `Service Account for the GCP project`: Also knows as DM Service Account,
      this SA needs permissions to all APIs DMs uses to create resources.
3. Cloud Foundation Toolkit
    - CFT must be installed in the Jenkins master and slaves. For installation
      intructions, look into the [User
      Guide](../docs/userguides.md#toolkit-installation-and-configuration)
    - Notice that [gcloud sdk](https://cloud.google.com/sdk) is a requirement
      for CFT
4. Environment Variables file
    - An example file is [here](pipeline-vars). Substitute the <FIXME:XXX> with
      values specific to you organization, and move the file to the Jenkins
      user's home directory

## Pipelines

This directory implements deployment pipelines showing how CFT can be used in
an *ficticious company*. In this ficticious company, it is assumed that 3
separate teams are responsible for sweparate pieces of the cloud
infrastructure:

- Central Cloud Platform Team:
    - Responsible for creating GCP projects, IAM entities, Permissions,
      Billing, etc
    - This team owns the pipeline and configs in the [project](project)
- Central Networking Team
    - Responsible for networking between for all other teams, interconnects,
      on-prem integration, etc
    - This team owns the pipeline and configs in the [network](network)
- Application Team
    - Each application team is reponsible for deploying their own application
      stacks. In this example, there's a single application team responsible
      for deploying its own GKE clusters in different environments.
    - This team owns the pipeline and configs in the [app](app)


Each folder in this directory represents and implements pipelines for each of
these teams above.
Notice that this is not an usual way of organizing Jenkins pipelines. Normally,
each pipeline is under its own git repo with it's own access controls for
different teams, but since this is a simple demonstration, each pipeline is in
a subfolder in the same repo.

