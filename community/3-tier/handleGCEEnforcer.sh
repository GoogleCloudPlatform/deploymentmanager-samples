#!/bin/bash
. vars.properties
. dmFunctions.sh

echo_mesg "Deleting previos firewall rule deployments"
deleteDeploymentAsync cities-service-lb-fw &
deleteDeploymentAsync cities-ui-lb-fw &
deleteDeploymentAsync cities-ui-fw &
wait

echo_mesg "Creating Firewall Rules"
createFirewall-LBToTag cities-service $NETWORK $BE_PORT $BE_TAG
createFirewall-LBToTag cities-ui $NETWORK $FE_PORT $FE_TAG
createFirewall-TagToTag cities-ui $NETWORK $BE_PORT $FE_TAG $BE_TAG
waitForHealthyBackend cities-ui
