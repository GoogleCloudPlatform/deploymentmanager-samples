# CFT Integrator Guide

<!-- TOC -->

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Pipeline Development](#pipeline-development)
    - [CFT Configuration](#cft-configuration)
    - [Jenkins Job](#jenkins-job)
- [Pipeline Execution](#pipeline-execution)

<!-- /TOC -->

## Overview

You can use the Cloud Foundation toolkit (henceforth, CFT) as a standalone
solution, via its command line interface (CLI) – see
[CFT User Guide](userguide.md) for details. Alternatively, you can initiate
CFT actions via its API, from a variety of existing orchestration tools, or
from your own application.

This Integrator Guide describes one of the CFT integration scenarios, wherein
you initiate the CFT actions from Jenkins. This Guide uses as an example a
Jenkins-based  “sample pipeline” that is included in the CFT repository -
see [***](***).

`Note:` The Jenkins-based process is for demonstration purposes only. It is not
intended as a product. Your Jenkins setup is likely to be different for the one
we use/demonstrate; therefore, to achieve similar results, you will need to
modify all the demo files.

## Prerequisites

1.	Install and configure Jenkins. For procedure, see ***.
2.	*** Anything else? ***

## Pipeline Development

Your pipeline must enable initiation of the following CFT actions:

- Deployment creation
- Deployment update
- Deployment deletion

In the sample pipeline, we deploy the *** config files (see ***), which are
related to each other as follows:

- *** is the “root” (does not depend on any other configs/deployments)
- *** depends on ***
- *** depends on ***
- ***

### CFT Configuration
To make CFT expose the config/deployment dependency graph as a parseable output
for Jenkins to consume:

1.	Do ***.
2.	Do ***.

### Jenkins Job

To enable the Jenkins to run the CFT actions:

1. Create a “seed job” Jenkinsfile that creates other jobs based on the
   dependency graph exposed by the CFT. For example:

```jenkins
*** Code of the “seed job” ***
```

When executed, the seed job will create a “final” job for each config-
containing directory that is submitted to the seed job. For example:

```jenkins
*** Code of the “final” job” ***
```

2. *** Anything else? ***

## Pipeline Execution

To execute a CFT action via Jenkins:

1. Execute the seed job in Jenkins: *** how, specifically? ***.

The seed job creates the “final” jobs. The final jobs run in the sequence
defined by the dependency graph. Each CFT stage (that corresponds to a
dependency level) is automatically translated to a Jenkins execution stage,
and is displayed in the Jenkins UI. For example:

```jenkins
*** Provide an example of what is displayed in Jenkins ***
```

2. Do *** anything else? ***.
