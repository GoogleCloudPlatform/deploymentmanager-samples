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

"""Creates an internally load balanced micro-service."""


def GenerateConfig(context):
  """Generates config."""

  prefix = context.env['deployment'] + '-' + context.env['name']
  service_name = prefix + '-service'
  lb_name = prefix + '-lb'
  endpoint_name = context.properties['endpoint']

  dm_samples_url = ''.join(['https://raw.githubusercontent.com/',
                            'GoogleCloudPlatform/deploymentmanager-samples/',
                            'master/examples/v2'])
  service_type_url = dm_samples_url + '/ha-service/service.py'
  lb_type_url = dm_samples_url + '/internal-lb/internal-lb.py'

  port = context.properties['port']
  default_network = ''.join(['https://www.googleapis.com/compute/v1/projects/',
                             context.env['project'],
                             '/global/networks/default'])

  resources = [{
      'name': service_name,
      'type': service_type_url,
      'properties': {
          'containerImage': context.properties['containerImage'],
          'dockerImage': context.properties['dockerImage'],
          'dockerEnv': context.properties['dockerEnv'],
          'port': port,
          'zone': context.properties['zone']
      }
  }, {
      'name': lb_name,
      'type': lb_type_url,
      'properties': {
          'groups': [
              '$(ref.' + service_name + '.group)'
          ],
          'app-port': port,
          'port': port,
          'zone': context.properties['zone']
      }
  }, {
      'name': endpoint_name,
      'type': 'serviceregistry.v1alpha.endpoint',
      'properties': {
          'addresses': [
              {'address': '$(ref.' + lb_name + '.address)'}
          ],
          'dnsIntegration': {
              'networks': [
                  default_network
              ]
          }
      }
  }]

  return {
      'resources': resources,
      'outputs': [{
          'name': 'service',
          'value': '$(ref.' + endpoint_name + '.name)'
      }]
  }
