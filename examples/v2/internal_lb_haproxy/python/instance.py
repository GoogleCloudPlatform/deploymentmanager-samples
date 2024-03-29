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

"""Creates a Compute Instance with the provided metadata."""


import six

COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'


def GlobalComputeUrl(project, collection, name):
  return ''.join([COMPUTE_URL_BASE, 'projects/', project,
                  '/global/', collection, '/', name])


def ZonalComputeUrl(project, zone, collection, name):
  return ''.join([COMPUTE_URL_BASE, 'projects/', project,
                  '/zones/', zone, '/', collection, '/', name])


def GenerateConfig(context):
  """Generate configuration."""

  base_name = context.env['deployment'] + '-' + context.env['name']

  items = []
  for key, value in six.iteritems(context.properties['metadata']):
    items.append({
        'key': key,
        'value': value
        })

  items.append({
      'key': 'startup-script',
      'value': context.imports[context.properties['startup-script']]
      })
  metadata = {'items': items}

  # Properties for the container-based instance.
  instance = {
      'zone': context.properties['zone'],
      'machineType': ZonalComputeUrl(
          context.env['project'], context.properties['zone'], 'machineTypes',
          context.properties['machine-type']),
      'metadata': metadata,
      'disks': [{
          'deviceName': 'boot',
          'type': 'PERSISTENT',
          'autoDelete': True,
          'boot': True,
          'initializeParams': {
              'diskName': base_name + '-disk',
              'sourceImage': GlobalComputeUrl(
                  'debian-cloud', 'images',
                  'family/debian-11')
              },
          }],
      'networkInterfaces': [{
          'accessConfigs': [{
              'name': 'external-nat',
              'type': 'ONE_TO_ONE_NAT'
              }],
          'network': GlobalComputeUrl(
              context.env['project'], 'networks', 'default')
          }],
      'serviceAccounts': [{
          'email': 'default',
          'scopes': [
              'https://www.googleapis.com/auth/compute.readonly',
              'https://www.googleapis.com/auth/cloud.useraccounts.readonly',
              'https://www.googleapis.com/auth/devstorage.read_only',
              'https://www.googleapis.com/auth/logging.write',
              'https://www.googleapis.com/auth/monitoring.write'
              ]
          }]
      }

  return {
      'resources': [{
          'name': base_name,
          'type': 'compute.v1.instance',
          'properties': instance
      }],
      'outputs': [{
          'name': 'address',
          'value': '$(ref.' + base_name + '.networkInterfaces[0].networkIP)'
      }]
  }

