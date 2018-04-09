#!/bin/bash 

# Author: Sufyaan Kazi
# Date: March 2018
# Purpose: Removes the $BE_TAG and $FE_TAG deployments

. vars.properties

##
# Removes bucket
#
deleteBucket() {
  local BUCKET_NAME=$PROJECT-$APP
  echo "Deleting bucket"
  gsutil rm -raf gs://${BUCKET_NAME}/*
  gsutil rb -f gs://${BUCKET_NAME}/
}

##
# Wrapper method to delete a deployment.
#
# The method redirects all output to null and runs the command as nohup, so that even if the script is killed
# the delete action will then still try to complete cleanly in the background asynchronusly. If th escript isn't terminated,
# the method will not end till the background task completes, so that any other deployments being deleted won't fail because
# of parent/child depndency relationships between deployments.
###
deleteDeployment() {
  EXIST=`echo $DEPS | grep $1 | wc -l`

  if [ $EXIST -ne 0 ]
  then
    echo "Deleting Deployment: $1"
    nohup gcloud deployment-manager deployments delete -q $1 > /dev/null  &
    wait
  fi
}

###
# Wrapper method to delete a deployment using the async flag.
#
# All output is sent to null and it the comand is executed as nohup
###
deleteDeploymentAsync() {
  EXIST=`echo $DEPS | grep $1 | wc -l`

  if [ $EXIST -ne 0 ]
  then
    echo "Deleting Deployment: $1"
    nohup gcloud deployment-manager deployments delete -q $1 --async > /dev/null 2>&1 &
  fi
}

###
# Deletes the $BE_TAG microservice
###
deleteBE() {
  deleteDeploymentAsync $BE_TAG-lb-fw
  deleteDeployment $BE_TAG-lb-fwd-rule
  deleteDeployment $BE_TAG-lb
  deleteDeployment $BE_TAG-ig-as
  deleteDeployment $BE_TAG-ig
  deleteDeploymentAsync $BE_TAG-lb-hc 
  deleteDeployment $BE_TAG-it
}

###
# Deletes the $FE_TAG microservice
###
deleteFE() {
  deleteDeploymentAsync $FE_TAG-fw
  deleteDeploymentAsync $FE_TAG-lb-fw
  deleteDeployment $FE_TAG-ig-as 
  deleteDeployment $FE_TAG-lb-fe
  deleteDeployment $FE_TAG-lb-web-proxy
  deleteDeployment $FE_TAG-lb-url-map
  deleteDeployment $FE_TAG-lb-be
  deleteDeployment $FE_TAG-ig
  deleteDeploymentAsync $FE_TAG-lb-hc
  deleteDeploymentAsync $FE_TAG-it
}

###
# Delete GCE Enforcer stuff
###
deleteGCEEnforcerStuff() {
  echo "Deleting GCE Enforcer and a.n.other firewall rules"

  local pids=""
  local RULES=$(gcloud compute firewall-rules list | grep $NETWORK | cut -d ' ' -f1 | xargs)
  for RULE in $RULES
  do
    echo "Deleting firewall rule: $RULE"
    gcloud compute firewall-rules delete $RULE -q >/dev/null 2>&1 &
    pids="$pids $!"
  done
  echo $pids
  wait $pids
}

###
# Delete network and subnets
###
deleteVPCStuff() {
  deleteGCEEnforcerStuff
  deleteDeployment $APP-$SUBNET
  deleteDeployment $APP-$NETWORK
}

echo "********* Performing Cleanup if necessary *****"
DEPS=`gcloud deployment-manager deployments list`
deleteFE &
deleteBE &
wait
deleteVPCStuff &
wait
gcloud deployment-manager deployments list
deleteBucket 
#gcloud projects delete $PROJECT -q
echo "********* Cleanup Complete *****"
