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
"""Creates an autoscaled managed instance group."""
# This consists of multiple resources:
# - Instance Template to define the properties for each VM
#      The image and machine size are hardcoded. They could be parameterized
# - Instance Group Manager
# - Autoscaler to grow and shrink the size of the the Instance Group
# - Load Balancer to distribute traffice to the VMs.


URL_BASE = 'https://www.googleapis.com/compute/v1/projects/'

# Every Python Template needs to have the GenerateConfig() or generate_config()
# method
# This method is called by DM in expansion and must return either:
#    - the yaml format required by DM
#    - a python dictionary representing the yaml (this is more efficient)


def GenerateConfig(context):
  """Generates the configuration."""

  deployment = context.env['deployment']
  instance_template = deployment + '-it'
  igm = deployment + '-igm'
  region = context.properties['region']
  port = context.properties['port']
  tp_name = deployment + '-tp'
  fr_name = deployment + '-fr'

  # Create a dictionary which represents the resources
  # (Intstance Template, IGM, etc.)
  resources = [
      {
          # Create the Instance Template
          'name': instance_template,
          'type': 'compute.v1.instanceTemplate',
          'properties': {
              'properties': {
                  'machineType':
                      'f1-micro',
                  'networkInterfaces': [{
                      'network':
                          URL_BASE + context.env['project'] +
                          '/global/networks/default',
                      'accessConfigs': [{
                          'name': 'External NAT',
                          'type': 'ONE_TO_ONE_NAT'
                      }]
                  }],
                  'disks': [{
                      'deviceName': 'boot',
                      'type': 'PERSISTENT',
                      'boot': True,
                      'autoDelete': True,
                      'initializeParams': {
                          'sourceImage':
                              URL_BASE +
                              'debian-cloud/global/images/family/debian-9'
                      }
                  }]
              }
          }
      },
      {
          # Instance Group Manager
          'name': igm,
          'type': 'compute.v1.regionInstanceGroupManager',
          'properties': {
              'region': region,
              'baseInstanceName': deployment + '-instance',
              'instanceTemplate': '$(ref.' + instance_template + '.selfLink)',
              'targetSize': 1,
              'autoHealingPolicies': [{
                  'initialDelaySec': 60
              }]
          }
      },
      {
          # Autoscaler
          'name': deployment + '-as',
          'type': 'compute.v1.regionAutoscaler',
          'properties': {
              'target': '$(ref.' + igm + '.selfLink)',
              'region': region,
              'autoscalingPolicy': {
                  'minNumReplicas': context.properties['minSize'],
                  'maxNumReplicas': int(context.properties['maxSize']),
                  'cpuUtilization': {
                      'utilizationTarget': 0.8
                  },
                  'coolDownPeriodSec': 90
              }
          }
      },
      {
          # Load Balancer - this is two resource: TargetPool & ForwardingRule
          'name': tp_name,
          'type': 'compute.v1.targetPool',
          'properties': {
              'region': region,
          }
      },
      {
          'name': fr_name,
          'type': 'compute.v1.forwardingRule',
          'properties': {
              'region': region,
              'portRange': port,
              'target': '$(ref.' + tp_name + '.selfLink)'
          }
      }
  ]

  return {'resources': resources}
