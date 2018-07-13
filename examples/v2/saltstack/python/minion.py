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

"""Creates a set of VMs each running a Salt minion daemon in a Docker container.
"""

IMAGE = ('https://www.googleapis.com/compute/v1/projects/debian-cloud'
         '/global/images/family/debian-9')


def GenerateConfig(context):
  """Generate final configuration."""

  resources = []
  for replica in range(0, context.properties['minionCount']):
    resources.append(GenerateInstanceConfig(context, replica))
  return {'resources': resources}


def GenerateInstanceConfig(context, replica):
  """Generate configuration for every minion instance."""

  name = (context.env['deployment'] + '-' + context.env['name'] + '-'
          + str(replica))

  machine_type = ('https://www.googleapis.com/compute/v1/projects/'
                  + context.env['project'] + '/zones/'
                  + context.properties['zone'] + '/machineTypes/f1-micro')
  instance = {
      'type': 'compute.v1.instance',
      'name': name,
      'properties': {
          'zone': context.properties['zone'],
          'machineType': machine_type,
          'disks': [{
              'deviceName': 'boot',
              'type': 'PERSISTENT',
              'boot': True,
              'autoDelete': True,
              'initializeParams': {
                  'sourceImage': IMAGE
              }
          }],
          'networkInterfaces': [{
              'network': ('https://www.googleapis.com/compute/v1/projects/'
                          + context.env['project']
                          + '/global/networks/default'),

              'accessConfigs': [{
                  'name': 'External NAT',
                  'type': 'ONE_TO_ONE_NAT'
              }]
          }],
          'tags': {
              'items': ['http-server']
          },
          'metadata': {
              'items': [{
                  'key': 'startup-script',
                  'value': ('#! /bin/bash\n'
                            'sudo echo \'deb http://debian.saltstack.com'
                            '/debian jessie-saltstack main\' >> '
                            '/etc/apt/sources.list\n'
                            'sudo wget -q -O- http://debian.saltstack.com/'
                            'debian-salt-team-joehealy.gpg.key | '
                            'sudo apt-key add -\n'
                            'sudo apt-get update\n'
                            'sudo apt-get -y install salt-minion\n'
                            'sudo sed -i \'s/#master: salt/master: ' +
                            context.properties['master'] +
                            '/\' /etc/salt/minion\n'
                            'sudo salt-minion -l debug')
              }]
          }
      }
  }
  return instance
