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
"""Creates autoscaled instance group with container image for each instance."""


def GenerateConfig(context):
  """Generate YAML resource configuration."""

  instance_template = context.env['deployment'] + '-it'
  igm = context.env['deployment'] + '-igm'
  image = ''.join(['https://www.googleapis.com/compute/v1/',
                   'projects/cos-cloud/global/images/',
                   context.properties['containerImage']])
  default_network = ''.join(['https://www.googleapis.com/compute/v1/projects/',
                             context.env['project'],
                             '/global/networks/default'])
  container_manifest = context.imports[context.properties['containerManifest']]
  network_interface = {'network': default_network}

  if context.properties['externalIp']:
    network_interface['accessConfigs'] = [{'name': 'External-IP',
                                           'type': 'ONE_TO_ONE_NAT'}]

  resources = [{
      'name': context.env['deployment'] + '-as',
      'type': 'compute.v1.autoscaler',
      'properties': {
          'zone': context.properties['zone'],
          'target': '$(ref.' + igm + '.selfLink)',
          'autoscalingPolicy': {
              'maxNumReplicas': context.properties['maxReplicas'],
              'cpuUtilization': {
                  'utilizationTarget': 0.8
              },
              'coolDownPeriodSec': 90
          }
      }
  }, {
      'name': igm,
      'type': 'compute.v1.instanceGroupManager',
      'properties': {
          'baseInstanceName': context.env['deployment'] + '-instance',
          'instanceTemplate': '$(ref.' + instance_template + '.selfLink)',
          'targetSize': context.properties['targetSize'],
          'zone': context.properties['zone']
      }
  }, {
      'name': instance_template,
      'type': 'compute.v1.instanceTemplate',
      'properties': {
          'properties': {
              'disks': [{
                  'deviceName': 'boot',
                  'type': 'PERSISTENT',
                  'boot': True,
                  'autoDelete': True,
                  'initializeParams': {
                      'sourceImage': image
                  }
              }],
              'machineType': context.properties['machineType'],
              'networkInterfaces': [network_interface],
              'metadata': {
                  'items': [{
                      'key': 'google-container-manifest',
                      'value': container_manifest
                  }]
              }
          }
      }
  }]

  return {'resources': resources}
