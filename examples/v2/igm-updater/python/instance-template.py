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

"""Creates autoscaled, network LB IGM running specified docker image."""


def GenerateConfig(context):
  """Generate YAML resource configuration."""

  resources = [{
      'name': context.env['name'],
      'type': 'compute.v1.instanceTemplate',
      'properties': {
          'properties': {
              'machineType': context.properties['machineType'],
              'disks': [{
                  'deviceName': 'boot',
                  'boot': True,
                  'type': 'PERSISTENT',
                  'autoDelete': True,
                  'mode': 'READ_WRITE',
                  'initializeParams': {
                      'sourceImage': context.properties['image']
                  }
              }],
              'networkInterfaces': [{
                  'accessConfigs': [{
                      'name': 'external-nat',
                      'type': 'ONE_TO_ONE_NAT'
                  }],
                  'network': 'global/networks/default',
              }],
              'metadata': {
                  'items': [{
                      'key': 'startup-script',
                      'value': ''.join(['#!/bin/bash\n',
                                        'python -m SimpleHTTPServer 8080'])
                  }]
              }
          }
      }
  }]

  return {'resources': resources}
