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
for  `jinja`:
```bash
    gcloud deployment-manager deployments create ${NAME} \
    --template cluster.jinja \
    --api-options=api-options.yaml \    
    --properties clusterName:${CLUSTER_NAME},zone:${ZONE}
```

or for `python`:
```bash
    gcloud deployment-manager deployments create ${NAME} \
    --template cluster.py \
    --properties clusterName:${CLUSTER_NAME},zone:${ZONE}
```

For example,

```bash
gcloud deployment-manager deployments create ${NAME} \
    --template cluster.jinja  \
    --api-options=api-options.yaml \    
    --properties clusterName:${CLUSTER_NAME},zone:${ZONE} 
NAME                       TYPE                                   STATE      ERRORS  INTENT
dm-gke-cluster-1           container.v1.cluster                   COMPLETED  []
dm-gke-cluster-1-provider  deploymentmanager.v2beta.typeProvider  COMPLETED  []

OUTPUTS      VALUE
clusterType  dm-gke-cluster-1-provider
```

The default `yaml` configuration file has the `Name`,`CLUSTER_NAME`, and `ZONE` predefined with 
the settings above so as a quickstart, you can just run:

```bash
 gcloud deployment-manager deployments create ${NAME} --config cluster.yaml
```

This will create two resources:

* a GKE cluster named `${CLUSTER_NAME}`
* a Deployment Manager type-provider named `${CLUSTER_NAME}-provider`

Note the `clusterType` (in this case `dm-gke-cluster-1-provider`).  You can use this type in other deployments to manage kubernetes resources using the cluster API.

### 2. Deploying Kubernetes resources

Using `deployment.yaml`, create a `Deployment` and a `Service`
to the GKE cluster created in the last step.

First set
```bash
IMAGE=nginx
PORT=80
```

for  `jinja`
```bash
gcloud deployment-manager deployments create dm-service \
    --template deployment.jinja \
    --properties clusterType:${CLUSTER_NAME}-provider,image:${IMAGE},port:${PORT}

NAME                                    TYPE                                                                                                   STATE      ERRORS  INTENT
dm-service-deployment-jinja-deployment  mineral-minutia-820/dm-gke-cluster-1-provider:/apis/apps/v1/namespaces/{namespace}/deployments/{name}  COMPLETED  []
dm-service-deployment-jinja-service     mineral-minutia-820/dm-gke-cluster-1-provider:/api/v1/namespaces/{namespace}/services/{name}           COMPLETED  []
```

or for `python`:

```bash
$ gcloud deployment-manager deployments create dm-service \
    --template deployment.py \
    --properties clusterType:${CLUSTER_NAME}-provider,image:${IMAGE},port:${PORT}
```

As above, you can use the defaults for defined in `deployment.yaml` if you used the defaults `yaml` during cluster creation

```bash
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

```bash
$ gcloud deployment-manager deployments delete dm-service -q

$ kubectl get deployments
No resources found.
```

### Delete Cluster

```bash
$ gcloud deployment-manager deployments delete ${NAME} -q
```

## GCP permissions

The default service account `Deployment Manager` runs as is `projectNumber-compute@developer.gserviceaccount.com` with has `Editor` permissions on the project.
If you manage certain resource types (`ClusterRole`, etc), you will need to grant additional IAM permissions.  Specifically, add

 - `roles/container.admin (Kubernetes Engine Admin)`

to  the service account.

## Deploying CustomResourceDefinitions

If you want to deploy other dynamic k8s artifacts such as [CustomResourceDefinitions](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/#customresourcedefinitions), define the collection first for that resource and then the object itself.

For example, for `CustomResourceDefinitions`, create a cluster that supports [CustomResourcePublishOpenAPI](https://kubernetes.io/docs/tasks/access-kubernetes-api/custom-resources/custom-resource-definitions/#publish-validation-schema-in-openapi-v2).  At the time of writing `11/6/19`, you need a GKE cluster version of atleast `1.14.7` and the Alpha feature gate enabled.  If you are using GKE 1.15+, `CustomResourcePublishOpenAPI` is enabled by default so the alpha flag is not required.

```bash
$ gcloud deployment-manager deployments create ${NAME} \
    --template cluster.jinja \
    --properties clusterName:${CLUSTER_NAME},zone:${ZONE},initialClusterVersion:1.14.7,enableKubernetesAlpha:true

$ gcloud container clusters get-credentials $CLUSTER_NAME --zone $ZONE    
```

Then define the CRD

```bash
$ gcloud deployment-manager deployments create my-crd --template crd.jinja --properties clusterType:${CLUSTER_NAME}-provider
NAME                  TYPE                                                                                                               STATE      ERRORS  INTENT
my-crd-crd-jinja-crd  mineral-minutia-820/dm-gke-cluster-1-provider:/apis/apiextensions.k8s.io/v1beta1/customresourcedefinitions/{name}  COMPLETED  []

$ gcloud container clusters get-credentials dm-gke-cluster-1

$ kubectl get crd
NAME                                    CREATED AT
crontabs.stable.example.com             2019-05-17T20:59:52Z
```

Finally define the CRD instance

```bash
$ gcloud deployment-manager deployments create my-crd-instance --template crd-instance.jinja --properties clusterType:${CLUSTER_NAME}-provider

$ gcloud deployment-manager deployments list
    dm-1                      insert               DONE                 manifest-1572649527023  []
    my-crd                    insert               DONE                 manifest-1572650044724  []
    my-crd-instance           insert               DONE                 manifest-1572656117578  []

$ kubectl get crd
    NAME                                    CREATED AT
    crontabs.stable.example.com             2019-11-01T23:18:47Z

$ kubectl get crontab
    NAME                 AGE
    my-new-cron-object   2m30s
```

To delete the CRD instance and definition, apply

```
$ gcloud deployment-manager deployments delete my-crd-instance -q

$ kubectl get crontab
    No resources found.

$ gcloud deployment-manager deployments delete my-crd -q
```

Note, if you delete the CRD or CRD definition directly via `kubectl`, deployment manager's state will not be consistent with what the GKE cluster has.
