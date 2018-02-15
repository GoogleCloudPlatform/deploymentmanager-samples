# Metadata from file

## Overview
This is a [Google Cloud Deployment
Manager](https://cloud.google.com/deployment-manager/overview) template which
deploys a VM with metadata values imported from a file. Any metadata key can be
imported using this mechanism, but this example shows how to import a
`startup-script`.

**NOTE**: Files containing the metadata being used must be imported as part of
the Deployment Manager configuration!

This example of creating an instance is purposely simple to illustrate a
concept. You may want to experiment with exposing more properties to the VM, for
example to change the machine type, source image, or network.

## Properties
This template takes the following input properties:

*   `zone`: the Google Cloud Platform zone in which the VM should run
*   `metadata-from-file`: a map of metadata key to file name containing metadata
    value. The file name must match the name of a file that has been imported as
    part of the configuration.

**NOTE**: Replace ZONE_TO_RUN in 'config.yaml' with a specific zone.

For more details on properties of this template, see the [template
schema](python/instance.py.schema).
