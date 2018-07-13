# Copyright 2018 Google Inc. All rights reserved.
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

import yaml
"""Reads and uses properties from global_properties.yaml."""


def GenerateConfig(context):
  global_properties = yaml.load(context.imports['global_properties.yaml'])

  network_interface = {
      'network': 'global/networks/default',
  }
  if global_properties['experiments']['EnableExternalIp']:
    network_interface['accessConfigs'] = [{'type': 'ONE_TO_ONE_NAT'}]
  return {
      'resources': [{
          'name':
              '%s-%s' % (context.env['name'], 'prod'
                         if global_properties['env'] == 'PROD' else 'nonprod'),
          'type':
              'gcp-types/compute-v1:instances'
              if global_properties['experiments']['EnableGcpTypes'] else
              'compute.v1.instance',
          'properties': {
              'zone':
                  context.properties['zone'],
              'machineType':
                  'zones/%s/machineTypes/f1-micro' %
                  (context.properties['zone']),
              'networkInterfaces': [network_interface],
              'disks': [{
                  'boot': True,
                  'autoDelete': True,
                  'initializeParams': {
                      'sourceImage':
                          'projects/debian-cloud/global/images/family/debian-9'
                  }
              }]
          }
      }]
  }
