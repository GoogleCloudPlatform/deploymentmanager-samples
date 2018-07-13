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


"""Generates config for a VM running a SaltStack master."""

COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'


def GlobalComputeUrl(project, collection, name):
  return (COMPUTE_URL_BASE + 'projects/' + project + '/global/'
          + collection + '/' + name)


def ZonalComputeUrl(project, zone, collection, name):
  return (COMPUTE_URL_BASE + 'projects/' + project + '/zones/'
          + zone + '/' + collection + '/' + name)


def GenerateConfig(context):
  """Generate configuration."""

  master = context.env['name']
  project = context.env['project']
  zone = context.properties['zone']

  resources = [{
      'name': master + '-firewall',
      'type': 'compute.v1.firewall',
      'properties': {
          'network': GlobalComputeUrl(project, 'networks', 'default'),
          'sourceRanges': ['0.0.0.0/0'],
          'allowed': [{
              'IPProtocol': 'tcp',
              'ports': ['4505', '4506']
          }]
      }
  }, {
      'name': master,
      'type': 'compute.v1.instance',
      'properties': {
          'zone': zone,
          'machineType': ZonalComputeUrl(project, zone, 'machineTypes',
                                         'f1-micro'),
          'disks': [{
              'deviceName': 'boot',
              'type': 'PERSISTENT',
              'boot': True,
              'autoDelete': True,
              'initializeParams': {
                  'sourceImage': GlobalComputeUrl('debian-cloud', 'images',
                                                  'family/debian-9'),
              }
          }],
          'networkInterfaces': [{
              'network': GlobalComputeUrl(project, 'networks', 'default'),
              'accessConfigs': [{
                  'name': 'External NAT',
                  'type': 'ONE_TO_ONE_NAT'
              }]
          }],
          'metadata': {
              'items': [{
                  'key': 'startup-script',
                  'value': ('#! /bin/bash\n'
                            'sudo echo \'deb http://debian.saltstack.com/'
                            'debian wheezy-saltstack main\' >> '
                            '/etc/apt/sources.list\n'
                            'sudo wget -q -O- http://debian.saltstack.com/'
                            'debian-salt-team-joehealy.gpg.key | '
                            'sudo apt-key add -\n'
                            'sudo apt-get update\n'
                            'sudo apt-get -y install salt-master\n'
                            'sudo salt-master -l debug')
              }]
          }
      }
  }]

  return {'resources': resources}
