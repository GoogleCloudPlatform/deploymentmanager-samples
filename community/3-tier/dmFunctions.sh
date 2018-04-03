#!/bin/bash 

# Author: Sufyaan Kazi
# Date: March 2018
# Purpose: Utility functions ot be used deploying apps to Compute Engine

###
# Utility method to pretty print messages to the screen
###
echo_mesg() {
   echo ""
   echo "----- $1 ----"
}

###
# Utility method to extract a value from YAMl
###
getYAMLValue() {
  echo $1 | cut -d ':' | xargs -f2
}

###
# Wrapper of the gcloud method to create a deployment.
#
# Method checks the right number of args were supplied then calls the create deployment method
###
createDeployment() {
  if [ $# -ne 2 ]
  then
    echo "Not enough arguments supplied, please supply <deploymentName> <yaml_file>, received: $@"
    exit 1
  fi

  local NAME=$1
  local YAML=$2
  gcloud deployment-manager deployments create $NAME --config $YAML > /dev/null
}

###
# Wrapper of the gcloud method to create a deployment.
#
# Method checks the right number of args were supplied then calls the create deployment method
###
createDeploymentFromTemplate() {
  if [ $# -lt 2 ]
  then
    echo "Not enough arguments supplied, please supply <deploymentName> <jinja_file> <optional: property overrides>, received: $@"
    exit 1
  fi

  local NAME=$1
  local JINJA=$2
  gcloud deployment-manager deployments create $NAME --template $JINJA --properties $3 > /dev/null
}

###
# Creates VPC network and subnetworks
###
createVPCStuff() {
  if [ $# -lt 5 ]
  then
    echo "Not enough arguments supplied, please supply <deploymentName> <network> <subnet> <subnet_cidr> <region>, received: $@"
    exit 1
  fi

  local NAME=$1
  local NETWORK=$2
  local SUBNET=$3
  local SUBNET_CIDR=$4
  local REGION=$5

  # Create the network
  createDeploymentFromTemplate $NAME-$NETWORK regional-network.jinja network:$NETWORK

  # Create the subnetwork
  createDeploymentFromTemplate $NAME-$SUBNET subnet.jinja network:$NETWORK,subnet:$SUBNET,subnet_cidr:$SUBNET_CIDR,region:$REGION
}

###
# Method to Create an Instance Template
###
createInstanceTemplate() {
  if [ $# -ne 6 ]
  then
    echo "Not enough arguments supplied, please supply <deploymentName> <region> <network> <subnet> <project> <bucketname>, received: $@"
    exit 1
  fi

  local IT=$1-it
  local REGION=$2
  local NETWORK=$3
  local SUBNET=$4
  local PROJECT=$5
  local BUCKET_NAME=$6

  echo $BUCKET_NAME
  echo_mesg "Creating Instance Template: $IT"
  createDeploymentFromTemplate $IT it.jinja basename:$1,region:$REGION,network:$NETWORK,subnet:$SUBNET,project:$PROJECT,bucketname:$BUCKET_NAME
}

###
# Method which waits for a VM Instance to start.
#
# It loops until the status of the instances is "RUNNING"
###
waitForInstanceToStart(){
  local INSTANCE_NAME=$1
  local ZONE=`gcloud compute instances list | grep $INSTANCE_NAME | xargs | cut -d ' ' -f2`
  local STATUS=`gcloud compute instances describe $INSTANCE_NAME --zone=${ZONE} | grep "status:" | cut -d ' ' -f2`

  while [[ "$STATUS" != "RUNNING" ]]
  do
    echo "Sleeping while instance starts ...."
    sleep 10
    STATUS=`gcloud compute instances describe $INSTANCE_NAME --zone=${ZONE} | grep "status:" | cut -d ' ' -f2`
  done
}

###
#
# Method which grabs the console output for debugging.
#
###
getInstanceOutput() {
  local INST=$1
  local ZONE=`gcloud compute instances list | grep $INST | xargs | cut -d ' ' -f2`

  gcloud compute instances get-serial-port-output ${INST} --zone=${ZONE}
}

###
# A method to create Regional Instance Group
#
# The method creates the Instrance group and autoscaler. The function will override
# the region in the yamls supplied, but in the future we may use Jinja placeholders
###
createRegionalInstanceGroup() {
  if [ $# -ne 6 ]
  then
    echo "Not enough arguments supplied, please supply <deploymentName> <region> <projectname> <network> <subnet> <bucketname>, received: $@"
    exit 1
  fi
  
  local IG=$1-ig
  local REGION=$2
  local PROJECT=$3
  local NETWORK=$4
  local SUBNET=$5
  local BUCKET_NAME=$6

  createInstanceTemplate $1 $REGION $NETWORK $SUBNET $PROJECT $BUCKET_NAME

  echo_mesg "Creating Instance Group: $IG"
  createDeploymentFromTemplate $IG ig.jinja basename:$1,region:$REGION

  # Define Autoscaling for Instance Group
  echo_mesg "Setting up Autoscale for: $IG"
  createDeploymentFromTemplate $IG-as ig-as.jinja basename:$1,region:$REGION,project:$PROJECT
}

###
#
# Method that waits for the IP of a forwarding rule
#
# This method will wait until the forwarding rule of an external load balancer has been provided with an external IP,
# and can be used to confirm the load balancer is ready to serve traffic
###
waitForFWDIP() {
  # Get the IP of the TCP Forwarding Rule once it's been assigned
  local FWD_IP=`gcloud compute forwarding-rules list | grep $1 | xargs | cut -d ' ' -f 3`
  local FWD_LIST=""
  while [ -z $FWD_IP ]
  do
    echo "Waiting for IP of forwarding rule: $1-fwd-rule"
    sleep 10
    FWD_LIST=`gcloud compute forwarding-rules list | grep $1 | wc -l`
    if [ $FWD_LIST -eq 1 ]
    then 
      # Grab the ip
      FWD_IP=`gcloud compute forwarding-rules list | grep $1 | xargs | cut -d ' ' -f 3`
    fi
  done
  echo "IP of $1 Load Balancer is: $FWD_IP"
}

###
# Method to wait for backend of HTTP load balancer to be ready
###
waitForHealthyBackend() {  
  local COUNT=$(gcloud compute backend-services get-health $1 --global | grep healthState | grep ': HEALTHY' | wc -l)
  while [ $COUNT -eq 0 ]
  do
    echo "Waiting for Healthy State of Backend Instances of the HTTP Load Balancer: $COUNT"
    sleep 10
    COUNT=$(gcloud compute backend-services get-health $1 --global | grep healthState | grep ': HEALTHY' | wc -l)
  done
}

###
# A utiltiy wrapper method to create firewall rules between a load balancer and a tag
#
###
createFirewall-LBToTag() {
  local NETWORK=$2
  local PORT=$3
  local TARGET=$4

  echo_mesg "Creating Firewall Rule: $1"
  createDeploymentFromTemplate $1-lb-fw lb-fw.jinja basename:$1,network:$NETWORK,port:$PORT,target:$TARGET
  echo "Waiting for firewall rule to take effect ...."
  #gcloud compute firewall-rules list | grep $1-http
  sleep 3
}

###
# A utility wrapper method to create firewall rules between tags
#
###
createFirewall-TagToTag() {
  local NETWORK=$2
  local PORT=$3
  local SOURCE=$4
  local TARGET=$5
  
  echo_mesg "Creating Firewall Rule: $1"
  createDeploymentFromTemplate $1-fw fw.jinja basename:$1,network:$NETWORK,port:$PORT,source:$SOURCE,target:$TARGET
  echo "Waiting for firewall rule to take effect ...."
  #gcloud compute firewall-rules list | grep $1-http
  sleep 3
}

###
# Utility method to ensure a URL returns HTTP 200
#
# When a HTTP load balancer is defined, there is a period of time needed to ensure all netowrk paths are clear
# and the requests result in happy requests.
###
checkAppIsReady() {
  #Check app is ready
  local URL=$1
  local HTTP_CODE=$(curl -Is http://${URL}/ | grep HTTP | cut -d ' ' -f2)
  while [ $HTTP_CODE -ne 200 ]
  do
    echo "Waiting for app to become ready: $HTTP_CODE"
    sleep 10
    HTTP_CODE=$(curl -Is http://${URL}/ | grep HTTP | cut -d ' ' -f2)
  done
}

###
# Method to create an Internal Load Balancer
#
# The method:
#   - creates the internal load balancer and healthcheck
#   - links the two together
#   - Creates the Backend for the Load Balancer from the associated Instance Group
#   - Creates forwarding rules for the frontend
#   - Waits for the internal load balancer to be ready and then atleast one instance of the backends to be readyA
#
# The method assumes a commong naming theme for the yamls of all components and deployment names, for simplicity.
###
createIntLB() {
  if [ $# -ne 7 ]
  then
    echo "Not enough arguments supplied, please supply <deploymentName> <targetregion> <project> <network> <subnet> <port> <request_path>, received: $@"
    exit 1
  fi

  local LB=$1-lb
  local REGION=$2
  local PROJECT=$3
  local NETWORK=$4
  local SUBNET=$5
  local PORT=$6
  local REQUEST_PATH=$7

  echo_mesg "Creating HealthCheck for the Internal Load Balancer: $LB"
  createDeploymentFromTemplate $LB-hc lb-hc.jinja basename:$1,port:$PORT,requestPath:$REQUEST_PATH

  echo_mesg "Creating Internal load balancer: $LB"
  createDeploymentFromTemplate $LB lb.jinja basename:$1,region:$REGION

  echo_mesg "Defining Backend service (Instance Group) for Internal Load Balancer: $LB"
  gcloud compute backend-services add-backend $LB --instance-group=$1-ig --instance-group-region=$2 --region=$2

  echo_mesg "Defining Forwarding Rule for Internal Load Balancer: $LB"
  createDeploymentFromTemplate $LB-fwd-rule lb-fwd-rule.jinja basename:$1,project:$PROJECT,region:$REGION,lb:$LB,network:$NETWORK,port:$PORT,region:$REGION,subnet:$SUBNET

  waitForFWDIP $LB

  local INSTANCE_NAME=`gcloud compute instances list | grep $1-ig | cut -d ' ' -f1 | head -n 1`
  waitForInstanceToStart $INSTANCE_NAME
}

###
# Method to create an External HTTP Load Balancer
#
# This method creates a healthcheck, backend service, URL Map, Web Proxy and Web Frontend, i.e. components needed for an external HTTP load balancer.
# The mothod completes when the vm instances in the backend are have initialised and have begun to report their status. Note this does not necessarily
# mean the instances are ready and healthy, just that they are ALMOST ready
###
createExtLB() {
  if [ $# -ne 4 ]
  then
    echo "Not enough arguments supplied, please supply <deploymentName> <region> <requestPath>, received: $@"
    exit 1
  fi

  local LB=$1-lb
  local REGION=$2
  local PORT=$3
  local REQUEST_PATH=$4

  echo_mesg "Creating Healthcheck: $1"
  createDeploymentFromTemplate $LB-hc http-hc.jinja basename:$1,port:$PORT,requestPath:$REQUEST_PATH

  echo_mesg "Creating Backend Service: $1"
  createDeploymentFromTemplate $LB-be be.jinja basename:$1,region:$REGION,port:$PORT

  echo_mesg "Creating URL Map: $1"
  createDeploymentFromTemplate $LB-url-map url-map.jinja basename:$1

  echo_mesg "Creating Web Proxy: $1"
  createDeploymentFromTemplate $LB-web-proxy web-proxy.jinja basename:$1

  echo_mesg "Creating Web FE: $1"
  createDeploymentFromTemplate $LB-fe fe.jinja basename:$1,region:$REGION

  waitForFWDIP $LB
}
