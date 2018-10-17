# Cloud Foundation Toolkit Project and Repository

## Overview

The Cloud Foundation toolkit (henceforth, CFT) includes the following parts:

- A comprehensive set of production-ready resource templates that follow
  Google's best practices, which can be used with the CFT or the gcloud
  utility (part of the Google Cloud SDK) - see Template Developer Guide(../docs/template_dev_guide.md)
- A command-line interface (henceforth, CLI) that deploys resources defined in
  single or multiple CFT-compliant config files - see the
  [CFT User Guide](../docs/userguide.md)
- A sample pipeline that enables running CFT deployment operations from
  Jenkins - see the [CFT Integrator Guide](*** does not exist yet ***)

## Repository Structure

The CFT project repository contains the following files and directories:

- Root:
  - README.md - this file
  - LICENSE - ***
  - Makefile - ***
  - MANUFEST - ***
  - src:
    - ...
  - docs:
    - userguide.md - the CFT guide for those users who are planning to use it
      "as is"
    - template_dev_guide.md - the CFT guide for those developers who are
      planning to modify the existing templates and/or create their own
    - tool_dev_guide.md - the CFT guide for those developers who are planning
      to modify, or integrate with, the deployment tool  
  - templates
  - ...

## License

Apache 2.0 - See [LICENSE](LICENSE) for more information.