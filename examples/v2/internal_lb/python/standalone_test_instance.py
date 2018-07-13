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
"""Creates a simple test instance you can SSH to."""

TARGET_TAG = 'standalone'
SOURCE_IMAGE = ('https://www.googleapis.com/compute/v1/'
                'projects/debian-cloud/global/images/family/'
                'debian-9')


def GenerateConfig(context):
  """Build a simple SSH ready test instance.

  Args:
    context: The context object provided by Deployment Manager.

  Returns:
    A config object for Deployment Manager (basically a dict with resources).
  """
  properties = context.properties
  resources = []

  resources.append({
      'name':
          context.env['deployment'] + '-standalone-instance-' +
          properties['zone'],
      'type':
          'compute.v1.instance',
      'properties': {
          'zone':
              properties['zone'],
          'machineType':
              'projects/{}/zones/{}/machineTypes/f1-micro'.format(
                  context.env['project'], properties['zone']),
          'tags': {
              'items': [TARGET_TAG],
          },
          'networkInterfaces': [{
              'network':
                  properties['network'],
              'subnetwork':
                  properties['subnet'],
              'accessConfigs': [{
                  'name': 'External NAT',
                  'type': 'ONE_TO_ONE_NAT'
              }]
          }],
          'disks': [{
              'type': 'PERSISTENT',
              'boot': True,
              'mode': 'READ_WRITE',
              'autoDelete': True,
              'deviceName': 'boot',
              'initializeParams': {
                  'sourceImage': SOURCE_IMAGE,
              }
          }],
      }
  })

  resources.append({
      'name':
          context.env['deployment'] + '-allow-ssh-to-standalone-' +
          properties['zone'],
      'type':
          'compute.v1.firewall',
      'properties': {
          'network': properties['network'],
          'allowed': [{
              'IPProtocol': 'tcp',
              'ports': ['22']
          }],
          'targetTags': [TARGET_TAG],
      }
  })
  return {'resources': resources}
