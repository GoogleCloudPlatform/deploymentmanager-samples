# GKE Cluster and Type

## Overview

This is a [Google Cloud Deployment Manager](https://cloud.google.com/deployment-manager/overview) template which deploys a GKE cluster and a [Deployment Manager type provider](https://cloud.google.com/deployment-manager/docs/configuration/type-providers/creating-type-provider). The type can be used by other deployments to manage Kubernetes resources in cluster.

This version uses the [OpenAPI 2.0 endpoint](https://kubernetes.io/docs/concepts/overview/kubernetes-api/#openapi-and-swagger-definitions) (`/openapi/v2`) and allows you to automatically acquire any GKE resource from one type-provider.  For example, once the cluster is created, you can manage any k8s artifact such as `Deployments`, `Services`, `DaemonSets` or even `CustomResourceDefinitions`

## Getting started

Using Deployment Manager to deploy Kubernetes resources into a new GKE cluster
is a two step process as described below: 

1. Create the GKE Cluster and Type-Provider
2. Use the Type-Provider to define a collection of the resource type you want to manage.

You can deploy using eihter the `jinja` or `python` Deployment Manager templates for either step.

### 1. Deploy a cluster

When ready, deploy with the following command:

```bash
NAME="dm-1"
CLUSTER_NAME="dm-gke-cluster-1"
ZONE="us-central1-a"
```
-  jinja:
```
    gcloud deployment-manager deployments create ${NAME} \
    --template cluster.jinja \
    --properties clusterName:${CLUSTER_NAME},zone:${ZONE}
```

or

- python:
```
    gcloud deployment-manager deployments create ${NAME} \
    --template cluster.py \
    --properties clusterName:${CLUSTER_NAME},zone:${ZONE}
```

For example,

```bash
gcloud deployment-manager deployments create ${NAME} \
    --template cluster.jinja  \
    --properties clusterName:${CLUSTER_NAME},zone:${ZONE} 
NAME                       TYPE                                   STATE      ERRORS  INTENT
dm-gke-cluster-1           container.v1.cluster                   COMPLETED  []
dm-gke-cluster-1-provider  deploymentmanager.v2beta.typeProvider  COMPLETED  []

OUTPUTS      VALUE
clusterType  dm-gke-cluster-1-provider
```

The default `yaml` configuration file has the `Name`,`CLUSTER_NAME`, and `ZONE` predefined with 
the settings above so as a quickstart, you can just run:

```
 gcloud deployment-manager deployments create ${NAME} --config cluster.yaml
```

This will create two resources:

* a GKE cluster named `${CLUSTER_NAME}`
* a Deployment Manager type-provider named `${CLUSTER_NAME}-provider`

Note the `clusterType` (in this case `dm-gke-cluster-1-provider`).  You can use this type in other deployments to manage kubernetes resources using the cluster API.

### 2. Deploying Kubernetes resources

Using `deployment.yaml`, create a `Deployment` and a `Service`
to the GKE cluster created in the last step.

with `jinja`
```bash
IMAGE=nginx
PORT=80

gcloud deployment-manager deployments create dm-service \
    --template deployment.jinja \
    --properties clusterType:${CLUSTER_NAME}-provider,image:${IMAGE},port:${PORT}

NAME                                    TYPE                                                                                                   STATE      ERRORS  INTENT
dm-service-deployment-jinja-deployment  mineral-minutia-820/dm-gke-cluster-1-provider:/apis/apps/v1/namespaces/{namespace}/deployments/{name}  COMPLETED  []
dm-service-deployment-jinja-service     mineral-minutia-820/dm-gke-cluster-1-provider:/api/v1/namespaces/{namespace}/services/{name}           COMPLETED  []
```

or with `python`:

```bash
$ gcloud deployment-manager deployments create dm-service \
    --template deployment.py \
    --properties clusterType:${CLUSTER_NAME}-provider,image:${IMAGE},port:${PORT}
```

As above, you can use the defaults for defined in `deployment.yaml` if you used the defaults `yaml` during cluster creation

```
   gcloud deployment-manager deployments create dm-service --config deployment.yaml 
```

### Verifying Kubernetes Resources

First make your `kubectl` command-line tool is set up to communicate with the cluster you have deployed:

```bash
gcloud container clusters get-credentials ${CLUSTER_NAME} --zone ${ZONE}
```

Now you can see the resources that have been deployed using `kubectl`:

```bash
$ kubectl get deployments,services
NAME                                                           DESIRED   CURRENT   UP-TO-DATE   AVAILABLE   AGE
deployment.extensions/dm-service-deployment-jinja-deployment   1         1         1            1           3m

NAME                                          TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
service/dm-service-deployment-jinja-service   NodePort    10.27.249.72   <none>        80:32028/TCP   3m
service/kubernetes                            ClusterIP   10.27.240.1    <none>        443/TCP        27m
```

### Delete Kubernetes Resources

```
$ gcloud deployment-manager deployments delete dm-service -q
Delete operation operation-1550337146155-58205fee0f097-edbb49e0-f337e0df completed successfully.

$ kubectl get deployments
No resources found.
```

### Delete Cluster

```
$ gcloud deployment-manager deployments delete ${NAME} -q
```

## GCP permissions

The default service account `Deployment Manager` runs as is `projectNumber-compute@developer.gserviceaccount.com` with has `Editor` permissions on the project.
If you manage certain resource types (`ClusterRole`, etc), you will need to grant additional IAM permissions.  Specifically, add

 - `roles/container.admin (Kubernetes Engine Admin)`

to  the service account.

## Deploying other types

If you want to deploy any other k8s artifact, create a collection reference and apply the [k8s API specifications](https://raw.githubusercontent.com/kubernetes/kubernetes/master/api/openapi-spec/swagger.json) for that resource.

For example, for `CustomResourceDefinitions`,

```
$ gcloud deployment-manager deployments create my-crd --template crd.jinja --properties clusterType:${CLUSTER_NAME}-provider
NAME                  TYPE                                                                                                               STATE      ERRORS  INTENT
my-crd-crd-jinja-crd  mineral-minutia-820/dm-gke-cluster-1-provider:/apis/apiextensions.k8s.io/v1beta1/customresourcedefinitions/{name}  COMPLETED  []

$ kubectl get crd
NAME                                    AGE
backendconfigs.cloud.google.com         6m
crontabs.stable.example.com             19s
scalingpolicies.scalingpolicy.kope.io   6m

$ gcloud deployment-manager deployments delete my-crd -q

$ kubectl get crd
NAME                                    AGE
backendconfigs.cloud.google.com         7m
scalingpolicies.scalingpolicy.kope.io   7m
```
