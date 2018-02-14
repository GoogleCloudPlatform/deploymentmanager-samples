#!/bin/sh

if [ $# -eq 0 ]
  then
    echo "Usage: $0 <deployment_name>"
    exit 1
fi

MANIFEST_NAME=`gcloud deployment-manager deployments describe $1  --format="value(deployment.manifest.basename())"`
gcloud deployment-manager manifests describe $MANIFEST_NAME --deployment $1 --format="value(layout)" > /tmp/$1-layout.yaml

grep -A 1 "finalValue" /tmp/$1-layout.yaml 