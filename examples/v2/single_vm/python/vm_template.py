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

"""Create VM with a single disk.

Creates a Persistent Disk. Then creates an instance that attaches
that Persistent Disk as a data disk.
"""

COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'


def GenerateConfig(context):
  """Create instance with disks."""

  datadisk = 'datadisk-'+ context.env['deployment']
  resources = [{
      'type': 'compute.v1.disk',
      'name': datadisk,
      'properties': {
          'zone': context.properties['zone'],
          'sizeGb': 10,
          # Disk type is a full URI.  Example uses pd-standard
          # but pd-ssd can be used as well
          'type': ''.join([COMPUTE_URL_BASE, 'projects/',
                           context.env['project'], '/zones/',
                           context.properties['zone'],
                           '/diskTypes/pd-standard'])
      }
  }, {
      'type': 'compute.v1.instance',
      'name': 'vm-' + context.env['deployment'],
      'properties': {
          'zone': context.properties['zone'],
          'machineType': ''.join([COMPUTE_URL_BASE, 'projects/',
                                  context.env['project'], '/zones/',
                                  context.properties['zone'],
                                  '/machineTypes/f1-micro']),
          'metadata': {
              'items': [{
                  # For more ways to use startup scripts on an instance, see:
                  # https://cloud.google.com/compute/docs/startupscript
                  'key': 'startup-script',
                  'value': '#!/bin/bash\npython -m SimpleHTTPServer 8080'
              }]
          },
          'disks': [{
              'deviceName': 'boot',
              'type': 'PERSISTENT',
              'boot': True,
              'autoDelete': True,
              'initializeParams': {
                  'diskName': 'disk-' + context.env['deployment'],
                  'sourceImage': ''.join([COMPUTE_URL_BASE, 'projects/',
                                          'debian-cloud/global/',
                                          'images/family/debian-9'])}
          }, {
              # Specify the data disk to mount. The deviceName can be anything,
              # but by convention is typically set to the same name.
              # This is the value is used in
              # /dev/disk/by-id/google-<deviceName>.
              # If not set, it will be
              # /dev/disk/by-id/google-persisent-disk-<number>.
              'deviceName': 'datadisk',
              'type': 'PERSISTENT',
              'source': '$(ref.' + datadisk + '.selfLink)',
              'autoDelete': True
          }],
          'networkInterfaces': [{
              'network': ''.join([COMPUTE_URL_BASE, 'projects/',
                                  context.env['project'],
                                  '/global/networks/default']),
              'accessConfigs': [{
                  'name': 'External NAT',
                  'type': 'ONE_TO_ONE_NAT'
              }]
          }]
      }
  }]
  return {'resources': resources}
