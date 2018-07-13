# Copyright 2016 Google Inc. All rights reserved.
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

URL_BASE = 'https://www.googleapis.com/compute/v1/projects/'


def GenerateConfig(context):
  """Generate Configuration."""

  deployment = context.env['deployment']
  instance_template = deployment + '-it'
  igm = deployment + '-igm'

  resources = [{
      'name': instance_template,
      'type': 'compute.v1.instanceTemplate',
      'properties': {
          'zone': context.properties['zone'],
          'properties': {
              'machineType': 'f1-micro',
              'networkInterfaces': [{
                  'network': ''.join([URL_BASE, context.env['project'],
                                      '/global/networks/default']),
                  'accessConfigs': [{
                      'name': 'External NAT',
                      'type': 'ONE_TO_ONE_NAT'}]
              }],
              'disks': [{
                  'deviceName': 'boot',
                  'type': 'PERSISTENT',
                  'boot': True,
                  'autoDelete': True,
                  'initializeParams': {
                      'sourceImage': ''.join([URL_BASE,
                                              'debian-cloud/global/images/',
                                              'family/debian-9'])
                  }
              }]
          }
      }
  }, {
      'name': igm,
      'type': 'compute.v1.instanceGroupManager',
      'properties': {
          'baseInstanceName': deployment + '-instance',
          'instanceTemplate': ''.join(['$(ref.', instance_template,
                                       '.selfLink)']),
          'targetSize': int(context.properties['targetSize']),
          'zone': context.properties['zone']
      }
  }, {
      'name': deployment + '-as',
      'type': 'compute.v1.autoscaler',
      'properties': {
          'zone': context.properties['zone'],
          'target': '$(ref.' + igm + '.selfLink)',
          'autoscalingPolicy': {
              'maxNumReplicas': int(context.properties['maxReplicas']),
              'cpuUtilization': {
                  'utilizationTarget': 0.8
              },
              'coolDownPeriodSec': 90
          }
      }
  }]

  return {'resources': resources}
