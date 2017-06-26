# HAProxy Internal Load-balancer

## Overview

This is a [Google Cloud Deployment
Manager](https://cloud.google.com/deployment-manager/overview) template which
deploys a single VM running HAProxy to load balance over a set of Instance
Groups. It automatically supports:

* adding/removing groups to load balance over,
* groups which are scaled both manually or with an autoscaler.

**NOTE**: The HAProxy instance will automatically refresh its configuration
every minute under the following conditions:

* VMs are added or removed from the groups it monitors
* a group is added or removed from the list of groups it monitors

**This will cause a brief downtime while HAProxy restarts itself**.

**NOTE**: This load balancer is only internal as long as the `port` is not
exposed via firewall. Be sure that the project you are deploying to **DOES NOT**
have any firewalls which expose the `port` for the load balancer VM.

## Properties

The load balancer takes the following input properties:

* `algorithm`: the HAProxy load balancing algorithm to use (defaults to
  `roundrobin`).
* `app-port`: the port exposed by the worker servers being load balanced to.
* `port`: the port exposed by load balancer.
* `groups`: the list of Instance Group URLs which should be load balanced to.
* `machine-type`: the machine type to use for the load balancer VM.
* `zone`: the zone to use for the load balancer VM.

**NOTE**: Replace ZONE_TO_RUN in 'config.yaml' with a specific zone.

For more details on properties of this template, see the [template
schema](internal-lb.py.schema).

## How it works

This template passes the following information via instance metadata to the VM:

* algorithm
* ports
* groups

These are used during startup and periodically to regenerate the HAProxy
configuration.

A cron job runs every minute after startup which will regenerate the
configuration and restart the HAProxy service if the configuration has changed.
