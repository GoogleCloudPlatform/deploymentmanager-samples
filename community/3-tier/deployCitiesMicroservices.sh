#!/bin/bash 

# Author: Sufyaan Kazi
# Date: March 2018
# Purpose: Deploys cities-service and cities-ui microservices to Compute Engine

#Load in vars and common functions
. ./vars.properties
. ./dmFunctions.sh

##
# Wrapper method to create the VPC network for these microservices
###
createVPCNetwork() {
  echo_mesg "Creating network and subnet"
  createVPCStuff $APP $NETWORK $SUBNET $SUBNET_CIDR $APP_REGION
}

###
# Deploys the backend microservice: cities-service.
# This microservice reads city data from a database and exposes Restful endpoints for CRUD(ish) actions
#
# The function creates an instance template, instance group, autoscaling group, internal load balancer and healthcheck.
# The app spins up a basic in-mem db and loads in test data on first load. It can be configured ot use CloudSQL or a.n.other if needed.
###
deployCitiesService() {
echo ${BUCKET_NAME}
  echo_mesg "Deploying cities-service"

  ######### Copy Startup Script for cities-service
  gsutil cp -r startup-scripts/cities-service.sh gs://${BUCKET_NAME}/startup-scripts/cities-service.sh 

  ######### Create Instance Group for cities service
  createRegionalInstanceGroup cities-service ${APP_REGION} ${PROJECT} $NETWORK $SUBNET $BUCKET_NAME

  ######### Define Internal Load Balancer for cities-service
  createIntLB cities-service ${APP_REGION} ${PROJECT} $NETWORK $SUBNET $BE_PORT $BE_REQUEST_PATH

  echo ""
}

###
# Deploys the cities-ui Microservice.
# This microservice calls the cities-service endpoints to display nice graphical representation of the cities data.
#
# The app reads the URL or ip address of the backing microservice from an ENVIRONMENT variable (set dynamically on startup)
###
deployCitiesUI() {
  echo_mesg "Deploying cities-ui"

  ######### Copy startup script for cities-ui
  gsutil cp -r startup-scripts/cities-ui.sh gs://${BUCKET_NAME}/startup-scripts/cities-ui.sh

  ######### Create Instance Groups for cities ui
  createRegionalInstanceGroup cities-ui ${APP_REGION} ${PROJECT} $NETWORK $SUBNET $BUCKET_NAME
  echo "  .... Waiting for apt-get updates to complete and then applications to start for cities-ui .... "
  sleep 120

  ######### Create External Load Balancer
  createExtLB cities-ui $APP_REGION $FE_PORT $FE_REQUEST_PATH

  echo ""
}

###
# Utility function to define firewall rules.
# This function batches together firewall rules for both micorservices as GCE Enforcer may delete them while the
# deployment is runnning. 
#
# This should construct rules that:
#   - Enables traffic between the front-end HTTP load balancer (and healthchecks) to the cities-ui app (on port tcp:8080)
#   - Enables traffic between internal load balancer (and it's healthchecks) to the cities-service apps (on port tcp:8081)
#   - Enables traffic between the cities-ui layer and the cities-service layer (on port tcp:8081)
createFirewallRules() {
  echo_mesg "Creating Firewall Rules"
  createFirewall-LBToTag cities-service $NETWORK $BE_PORT $BE_TAG
  createFirewall-LBToTag cities-ui $NETWORK $FE_PORT $FE_TAG
  createFirewall-TagToTag cities-ui $NETWORK $BE_PORT $FE_TAG $BE_TAG
  waitForHealthyBackend cities-ui-lb-be
  sleep 3
  waitForHealthyBackend cities-ui-lb-be

  echo ""
}

SECONDS=0
BUCKET_NAME=$PROJECT-$APP

# Start
. ./cleanup.sh

echo_mesg "****** Deploying Microservices *****"
######## gcloud projects create $PROJECT 

######### Create Bucket
echo_mesg "Creating Bucket"
gsutil mb gs://${BUCKET_NAME}/

######## Create VPC Network and subnetwork
createVPCNetwork

######## Deploy Apps 
deployCitiesService
deployCitiesUI
createFirewallRules

######### Launching Browser
echo_mesg "Determining external URL of application"
URL=`gcloud compute forwarding-rules list | grep cities-ui | xargs | cut -d ' ' -f 2`
echo "  -> URL is $URL"
checkAppIsReady $URL
# GCE Enforcer is a bit of a bully sometimes and in addition the app needs to stabilise a bit
sleep 7
checkAppIsReady $URL
echo_mesg "Launching Browser: $URL"
open http://${URL}/

echo_mesg "********** App Deployed **********"

echo_mesg "Deployment Complete in $SECONDS seconds."
