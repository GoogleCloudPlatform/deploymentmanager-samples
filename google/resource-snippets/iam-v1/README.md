# Samples for provider gcp-types/iam-v1

## Overview

This folder contains [Google Cloud Deployment
Manager](https://cloud.google.com/deployment-manager/overview) samples for follwing types:

* gcp-types/iam-v1:projects.serviceAccounts
* gcp-types/iam-v1:projects.serviceAccounts.keys
* gcp-types/iam-v1:organizations.roles
* gcp-types/iam-v1:projects.roles

## Sample usage

### iam-v1-header-provider.yaml
This config creates a customized type provider for [IAM-v1 API](https://iam.googleapis.com/$discovery/rest?version=v1) which
can be used as a replacement for gcp-types/iam-v1 type provider and applies additional header mapping for Bearer token.
