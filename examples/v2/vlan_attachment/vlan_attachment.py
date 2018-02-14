def networkUrl(project_id, name):
  return 'https://www.googleapis.com/compute/v1/projects/%s/global/networks/%s' % (project_id, name)

def interconnectUrl(project_id, name):
  return 'https://www.googleapis.com/compute/v1/projects/%s/global/interconnects/%s' % (project_id, name)

def GenerateConfig(context):
  resources = []

  router_name = context.env['deployment'] + '-router'
  vlan_attach_name = context.env['deployment'] + '-vlan-attach'
  router_interface_name = router_name + '-if' 
  bgp_peer_name = router_interface_name + '-peer'

  # Adding Cloud Router
  resources.append({
    'name': router_name,
    'type': 'compute.v1.router',
    'properties': {
       'bgp': {
         'asn': context.properties['cr_asn']
       },
       'network': networkUrl(context.properties['vpc_project_id'], context.properties['vpc_name']),
       'region': context.properties['cr_region'],
      'project': context.properties['vpc_project_id']
     }
  })  

  # Adding VLAN attachment (also known as InterconnectAttachment)
  resources.append({
    'name': vlan_attach_name,
    'type': 'compute.v1.interconnectAttachments',
    'properties': {
      'region': context.properties['cr_region'],
      'router': '$(ref.' + router_name + '.selfLink)',
      'interconnect': interconnectUrl(context.properties['interconnect_project_id'], context.properties['interconnect_name'])
    }
  })

  #registering output values for a VLAN tag, customer router link local IP address and Google Cloud router link local IP address
  outputs = [
    {'name': 'vlan_tag',
     'value': '$(ref.' + vlan_attach_name + '.privateInterconnectInfo.tag8021q)'},
    {'name': 'customer_router_ip',
     'value': '$(ref.' + vlan_attach_name + '.customerRouterIpAddress)'},
    {'name': 'cloud_router_ip',
     'value': '$(ref.' + vlan_attach_name + '.cloudRouterIpAddress)'}]

  #add a Cloud Router interface that connects to the VLAN attachment
  resources.append({
    'name': router_interface_name,
    'action': 'gcp-types/compute-v1:compute.routers.patch',
    'properties': {
      'router': router_name,
      'region': context.properties['cr_region'],
      'project': context.properties['vpc_project_id'],
      'name': router_name,
      'interfaces': [{
        'ipRange': '$(ref.' + vlan_attach_name + '.cloudRouterIpAddress)',
        'linkedInterconnectAttachment': '$(ref.' + vlan_attach_name + '.selfLink)',
        'name': router_interface_name
      }]
    }
  })

  
  if 'peer_ip_address' in  context.properties: 
    # Add a BGP peer to the interface
    resources.append({
      'name': bgp_peer_name,
      'action': 'gcp-types/compute-v1:compute.routers.patch',
      'properties': {
        'router': router_name,
        'region': context.properties['cr_region'],
        'project': context.properties['vpc_project_id'],
        'name': router_name,
        'bgpPeers': [{
          'interfaceName': router_interface_name,
          'name': bgp_peer_name,
          'peerAsn': context.properties['peer_asn'],
          'peerIpAddress': context.properties['peer_ip_address']
        }]
      },
      'metadata': {'dependsOn': [router_interface_name]}
    })     

  return {'resources': resources, 'outputs': outputs}
  