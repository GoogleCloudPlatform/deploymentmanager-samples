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

"""Generates configuration for a single NAT gateway """


def GenerateConfig(context):
  """Generates config."""

  prefix = context.env['name']
  zone = context.properties['zone']

  resources = []

  #reserve a static IP address
  ip_name = prefix + '-ip'
  resources.append({
    'name': ip_name,
    'type': 'compute.v1.address',
    'properties': {
      'region': context.properties['region']
    }
  })  

  # create an instance template that points to a reserved static IP address
  template_name = prefix + '-it'
  runtime_var_name = prefix + '/0'  

  resources.append({
    'name': template_name,
    'type': 'compute.v1.instanceTemplate',
    'properties': {
      'properties': {
        'disks': [{
          'deviceName': 'boot',
          'type': 'PERSISTENT',
          'mode': 'READ_WRITE',
          'boot': True,
          'autoDelete': True,
          'initializeParams': {
            'sourceImage': context.properties['image'],
            'diskType': context.properties['diskType'],
            'diskSizeGb': context.properties['diskSizeGb']
          }
        }],
        'tags': {
          'items': [context.properties['nat-gw-tag']]
        },
        'machineType': context.properties['machineType'],
        'metadata': {
          'items': [{
            'key': 'startup-script',
            'value': context.properties['startupScript']
            },
            {
            'key': 'runtime-variable',
            'value': runtime_var_name
            },
            {
            'key': 'runtime-config',
            'value': context.properties['runtimeConfigName']
            },
          ]
        },
        'serviceAccounts': [{
          'email': 'default',
          'scopes': [
            # The following scope allows an instance to create runtime variable resources.
            'https://www.googleapis.com/auth/cloudruntimeconfig'
          ]
        }], 
        'canIpForward': True,
        'networkInterfaces': [{
          'network': context.properties['network'],
          'subnetwork': context.properties['subnetwork'],
        'accessConfigs': [{
          'name': 'External-IP',
          'type': 'ONE_TO_ONE_NAT',
          'natIP': '$(ref.' + ip_name + '.address)' }] 
        }]
      }
    }
  })

  # create an instance greoup manager of size 1  with autohealing enabled
  # it will make sure that the NAT gateway VM is always up
  igm_name = prefix + '-igm'
  resources.append({
    'name': igm_name,
    'type': 'compute.beta.instanceGroupManager',
    'properties': {
      'baseInstanceName': prefix + '-vm',
      'instanceTemplate': '$(ref.' + template_name + '.selfLink)',
      'targetSize': 1,
      'zone': zone,
      'autoHealingPolicies': [{
        'initialDelaySec': 120,
        'healthCheck': context.properties['healthCheck']
      }]
    }
  })

  # Wait until a GCE VM is created by the instance group manager. 
  waiter_name = prefix + '-waiter'
  resources.append({
    'name': waiter_name,
    'type': 'runtimeconfig.v1beta1.waiter',
    'properties': {
      'parent': context.properties['runtimeConfig'],
      'waiter': waiter_name,
      'timeout': '120s',
      'success': {
        'cardinality': {
          'path': prefix,
          'number': 1
        }
      }
    },
    'metadata': {
      'dependsOn': [igm_name]
    }
  })  

  # Find a name of the GCE VM created by the instance group manager
  get_mig_instances = prefix + '-get-mig-instances' 
  resources.append({
    'name': get_mig_instances,
    'action': 'gcp-types/compute-v1:compute.instanceGroupManagers.listManagedInstances',
    'properties': {
      'instanceGroupManager': igm_name,
      'project': context.properties['projectId'],
      'zone': zone,
    },
    'metadata': {
      'dependsOn': [waiter_name]
    }
  })

  #create a route that will allow to use the NAT gateway VM as a next hop
  route_name = prefix + 'route'
  resources.append({
    'name': route_name,
    'type': 'compute.v1.route',
    'properties': {
      'network': context.properties['network'],
      'tags': [context.properties['nated-vm-tag']],
      'destRange': '0.0.0.0/0',
      'priority': context.properties['routePriority'],
      'nextHopInstance': '$(ref.' + get_mig_instances + '.managedInstances[0].instance)'
    }
  }) 

  return {'resources': resources}