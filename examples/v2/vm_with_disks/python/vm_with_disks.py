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

"""Creates a VM with user specified disks attached to it."""

COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'


def DiskName(context, diskobj):
  return context.env['deployment'] + '-disk-' + diskobj['name']


def GenerateConfig(context):
  """Creates configuration."""

  resources = []
  project = context.env['project']

  # create disks resources
  for disk_obj in context.properties['disks']:
    resources.append({'name': DiskName(context, disk_obj),
                      'type': 'compute.v1.disk',
                      'properties': {
                          'zone': context.properties['zone'],
                          'sizeGb': str(disk_obj['sizeGb']),
                          'type': ''.join([COMPUTE_URL_BASE,
                                           'projects/', project, '/zones/',
                                           context.properties['zone'],
                                           '/diskTypes/', disk_obj['diskType']])
                      }
                     })
  disks = []
  disks.append({'deviceName': 'boot',
                'type': 'PERSISTENT',
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'diskName': project + '-boot',
                    'sourceImage': ''.join([COMPUTE_URL_BASE, 'projects/',
                                            'debian-cloud/global/images/',
                                            'family/debian-9'])
                }
               })
  for disk_obj in context.properties['disks']:
    disks.append({'deviceName': DiskName(context, disk_obj),
                  'type': 'PERSISTENT',
                  'source': ''.join(['$(ref.', DiskName(context, disk_obj),
                                     '.selfLink)']),
                  'autoDelete': True})

  # create vm with disks
  resources.append({'name': context.env['deployment'] + '-vm',
                    'type': 'compute.v1.instance',
                    'properties': {
                        'zone': context.properties['zone'],
                        'machineType': ''.join([COMPUTE_URL_BASE, 'projects/',
                                                project, '/zones/',
                                                context.properties['zone'],
                                                '/machineTypes/f1-micro']),
                        'networkInterfaces': [{
                            'network': ''.join([COMPUTE_URL_BASE,
                                                'projects/', project,
                                                '/global/networks/default']),
                            'accessConfigs': [{
                                'name': 'External NAT',
                                'type': 'ONE_TO_ONE_NAT'}],
                        }],
                        'disks': disks
                    }
                   })
  return {'resources': resources}
