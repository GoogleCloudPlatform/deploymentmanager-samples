# Copyright 2017 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'

class PropertyError(Exception):
  """An exception raised when property values are invalid."""


def GlobalComputeUrl(project, collection, name):
  return ''.join([COMPUTE_URL_BASE, 'projects/', project,
                  '/global/', collection, '/', name])

def RegionalComputeUrl(project, region, collection, name):
  return ''.join([COMPUTE_URL_BASE, 'projects/', project,
                  '/regions/', region, '/', collection, '/', name])

def ZonalComputeUrl(project, zone, collection, name):
  return ''.join([COMPUTE_URL_BASE, 'projects/', project,
                  '/zones/', zone, '/', collection, '/', name])

def _CheckZones(context):
  """Make sure that zones specified in deployment properties belong to the same region"""
  region = context.properties['region']  
  for zone in context.properties['zones']:
    if not zone.startswith(region):
      raise PropertyError('zone {} does not belong to  {} region'.format(zone, region))

def CheckParameters(context):
  """Check parameters of the deployment for semantics correctness """
  _CheckZones(context)
    
def GenerateConfig(context):
  """Generates deployment configuration """

  CheckParameters(context)

  prefix = context.env['deployment']

  hc_name = prefix + '-hc'
  fw_name = prefix + '-hc-fw'
  rt_config_name = prefix + '-config'

  project_id = context.properties['projectId']
  network_project_id = context.properties['networkProjectId']

  if (network_project_id == ''):
    network_project_id = project_id
  
  region = context.properties['region']
  nat_gw_tag = context.properties['nat-gw-tag'] 

  network = GlobalComputeUrl(network_project_id, 'networks', context.properties['network'])
  subnetwork = RegionalComputeUrl(network_project_id, region, 'subnetworks', 
    context.properties['subnetwork'])
  sourceImage =  GlobalComputeUrl('debian-cloud', 'images', 'family/debian-9')

  config = {'resources': []}

  # A health check to be used by managed instance groups
  healthCheck = {
      'name': hc_name,
      'type': 'compute.v1.httpHealthCheck',
      'properties': {
          'port': 80,
          'requestPath': '/health-check',
          'healthyThreshold': 1,
          'unhealthyThreshold': 3,
          'checkIntervalSec': 10
      }
  }
  config['resources'].append(healthCheck)

  # Firewall rule that allows the health check to work. See
  # https://cloud.google.com/compute/docs/load-balancing/health-checks#health_check_source_ips_and_firewall_rules.
  fwRule = {
      'name': fw_name,
      'type': 'compute.v1.firewall',
      'properties': {
          'network': network,
          'sourceRanges': ['209.85.152.0/22', '209.85.204.0/22', '35.191.0.0/16', '130.211.0.0/22'],
          'targetTags': [nat_gw_tag],
          'allowed': [{
              'IPProtocol': 'TCP',
              'ports': [80]
          }]
      }
  }
  config['resources'].append(fwRule)
  
  # Runtime config is used to coordinate waiters and make sure that NAT gateway VMs are up before trying 
  # to add routes pointing to these VMs
  rtConfig = {
      'name': rt_config_name,
      'type': 'runtimeconfig.v1beta1.config',
      'properties': {
          'config':  rt_config_name
      }
  }
  config['resources'].append(rtConfig)

  # Create a NAT gateway for each zone specified in zones property 
  i = 1
  for zone in context.properties['zones']:
    nat_gateway_vm = {
        # the same zone can be specified multiple times, so adding a counter for uniquness
        'name': prefix  + '-nat-' +  str(i) + '-' + zone ,
        'type': 'single-nat-gateway.py',
        'properties': {
            'projectId': project_id,
            'region': region,
            'zone': zone,
            'machineType': context.properties['machineType'],
            'image': sourceImage,
            'diskType': context.properties['diskType'],
            'diskSizeGb': context.properties['diskSizeGb'],
            'nat-gw-tag': context.properties['nat-gw-tag'],
            'nated-vm-tag': context.properties['nated-vm-tag'],
            'routePriority': context.properties['routePriority'],
            'startupScript': context.properties['startupScript'],
            'network': network,
            'subnetwork': subnetwork,
            'healthCheck': '$(ref.' + hc_name + '.selfLink)',
            'runtimeConfig': '$(ref.' + rt_config_name + '.name)',
            'runtimeConfigName': rt_config_name 
        }
    }
    config['resources'].append(nat_gateway_vm)
    i += 1

  return config
