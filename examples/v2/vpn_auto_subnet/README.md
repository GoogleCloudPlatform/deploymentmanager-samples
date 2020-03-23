# Cloud VPN with Auto Subnet Networks

Templated Cloud VPN deployment with an auto subnet network

## Prerequisites
- Install [gcloud](https://cloud.google.com/sdk)
- [Cloud VPN requirements](https://cloud.google.com/compute/docs/vpn/overview#requirements)
- Create a project, setup billing, enable requisite APIs in [Google Cloud Console](https://console.cloud.google.com/)

## Cloud VPN and Network Deployment

### Resources
- Network with auto subnets
- Static IP address
- VPN gateway
- Forwarding rules for ESP, UDP 500, UDP 4500
- VPN tunnel
- Firewall rules for inbound traffic
- Static route for outbound traffic

### Required properties:
- `region`
- `ikeVersion`
- `peerIp`
- `sharedSecret`
- `sourceRanges`
- `routeTag`

### Deployment

Creating the network and Cloud VPN:

    $ gcloud deployment-manager deployments create network-vpn-deployment \
    --template vpn-auto-subnet.jinja --project PROJECT_NAME \
    --properties "peerIp:PEER_VPN_IP,sharedSecret:SECRET,sourceRanges:PEERED_RANGE"

Deleting the network and Cloud VPN

    $ gcloud deployment-manager deployments delete network-vpn-deployment

