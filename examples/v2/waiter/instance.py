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

"""Creates a VM with the provided name, metadata, and auth scopes."""


COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'


def GlobalComputeUrl(project, collection, name):
  return ''.join([COMPUTE_URL_BASE, 'projects/', project,
                  '/global/', collection, '/', name])


def ZonalComputeUrl(project, zone, collection, name):
  return ''.join([COMPUTE_URL_BASE, 'projects/', project,
                  '/zones/', zone, '/', collection, '/', name])


def GenerateConfig(context):
  """Generate configuration."""

  base_name = context.properties['instanceName']

  items = []
  for key, value in context.properties['metadata'].iteritems():
    items.append({
        'key': key,
        'value': value
        })
  metadata = {'items': items}

  # Properties for the container-based instance.
  instance = {
      'zone': context.properties['zone'],
      'machineType': ZonalComputeUrl(
          context.env['project'], context.properties['zone'], 'machineTypes',
          'f1-micro'),
      'metadata': metadata,
      'serviceAccounts': [{
          'email': 'default',
          'scopes': context.properties['scopes']
      }],
      'disks': [{
          'deviceName': 'boot',
          'type': 'PERSISTENT',
          'autoDelete': True,
          'boot': True,
          'initializeParams': {
              'diskName': base_name + '-disk',
              'sourceImage': GlobalComputeUrl(
                  'debian-cloud', 'images',
                  ''.join(['backports-debian', '-7-wheezy-v20151104']))
              },
          }],
      'networkInterfaces': [{
          'accessConfigs': [{
              'name': 'external-nat',
              'type': 'ONE_TO_ONE_NAT'
              }],
          'network': GlobalComputeUrl(
              context.env['project'], 'networks', 'default')
          }]
      }

  # Resources and output to return.
  return {
      'resources': [{
          'name': base_name,
          'type': 'compute.v1.instance',
          'properties': instance
          }]
      }
