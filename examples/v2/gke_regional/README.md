# Regional cluster GKE

Template of regional GKE cluster with some bugs workarounds.


### Tricking the DM bugs/features in template


* https://issuetracker.google.com/issues/38131324:

tldr: You can not update nodePools in the cluster.

Workaround: We create one little nodePool of two preemtible f1-mciro instances because you can not create the cluster without nodePools at all. All the acutall nodePools that are going to run the load are defined as separate objects.

Due to this bug nodePool's update operation isn't atomic: You need to create new nodePool with the new options, cordon and drain the old one and delete it then.

* https://issuetracker.google.com/issues/72372261:

tld: there's no official announced regional cluster type.

Workaround: Use undocumented beta type: gcp-types/container-v1beta1:projects.locations.clusters

* https://issuetracker.google.com/issues/78369197:

tldr: there's no official announced nodePool type that would work with regional clusters.

Workaround: Use undocumented beta one: gcp-types/container-v1beta1:projects.locations.clusters.nodePools


### Example of the conifg

The config structure mostly repeat native GCP API objects structure.

```
imports:
- path: cluster.py

resources:
- name: my-cluster
  type: cluster.py
  properties:
    region: europe-west4
    network: $SELF_LINK_TO_NETWORK
    nodePools:
    - name: 'standard-1-4'
      config:
        machineType: n1-standard-4
        labels:
          role: k8s-node
          env: prod
          owner: infra-team
          bu: infrastructure-services
          impact: medium
          data: private
          type: n1-standard-4
      autoscaling:
        enabled: true
        minNodeCount: 2
        maxNodeCount: 10
    ipAllocationPolicy:
      useIpAliases: true
      createSubnetwork: true
      subnetworkName: 'my-cluster-eu-4'
      nodeIpv4CidrBlock: 10.9.0.0/22
      clusterIpv4CidrBlock: 10.16.0.0/14
      servicesIpv4CidrBlock: 10.8.32.0/20
```

This config will create two objects:
* Regional cluster with default node-pool of six (two per zone) f1-micro preemtible instances.
* Subnetwork in defined network with secondary ranges.
* Regional nodePool of n1-standard-4 type with all the properties described + default one from the schema. The nodePool is "attached" to the cluster.


### About schema

Schema is quite detailed, but not complete. It was create becaus IMO schema validation exceptions are way more readable than the exceptions that DM provide you with for the same error.
