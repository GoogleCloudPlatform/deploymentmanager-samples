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

"""Constructs a VM with imported module."""
from helpers import common

COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'


def GenerateConfig(context):
  """Generates configuration of a VM."""
  resources = [{
      'name': common.GenerateMachineName('myfrontend', 'prod'),
      'type': 'compute.v1.instance',
      'properties': {
          'zone': 'us-central1-f',
          'machineType': COMPUTE_URL_BASE + 'projects/' + context.env['project']
                         + '/zones/us-central1-f/machineTypes/f1-micro',
          'disks': [{
              'deviceName': 'boot',
              'type': 'PERSISTENT',
              'boot': True,
              'autoDelete': True,
              'initializeParams': {
                  'sourceImage': COMPUTE_URL_BASE + 'projects/'
                                 'debian-cloud/global/images/family/debian-9'}
          }],
          'networkInterfaces': [{
              'network': COMPUTE_URL_BASE + 'projects/' + context.env['project']
                         + '/global/networks/default',
              'accessConfigs': [{
                  'name': 'External NAT',
                  'type': 'ONE_TO_ONE_NAT'
              }]
          }]
      }
  }]
  return {'resources': resources}
