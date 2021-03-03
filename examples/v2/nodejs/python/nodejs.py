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

"""Create nodejs template with the back-end and front-end templates."""


def GenerateConfig(context):
  """Generate configuration."""

  backend = context.env['deployment'] + '-backend'
  frontend = context.env['deployment'] + '-frontend'
  firewall = context.env['deployment'] + '-application-fw'
  application_port = 8080
  mysql_port = 3306
  resources = [{
      'name': backend,
      'type': 'container_vm.py',
      'properties': {
          'zone': context.properties['zone'],
          'dockerImage': 'gcr.io/qwiklabs-resources/mysql',
          'containerImage': 'family/cos-stable',
          'port': mysql_port,
          'dockerEnv': {
              'MYSQL_ROOT_PASSWORD': 'mypassword'
          }
      }
  }, {
      'name': frontend,
      'type': 'frontend.py',
      'properties': {
          'zone': context.properties['zone'],
          'dockerImage': 'gcr.io/qwiklabs-resources/nodejsservice',
          'port': application_port,
          # Define the variables that are exposed to container as env variables.
          'dockerEnv': {
              'SEVEN_SERVICE_MYSQL_PORT': mysql_port,
              'SEVEN_SERVICE_PROXY_HOST': '$(ref.' + backend
                                          + '.networkInterfaces[0].networkIP)'
          },
          # If left out will default to 1
          'size': 2,
          # If left out will default to 1
          'maxSize': 20
      }
  }, {
      'name': firewall,
      'type': 'compute.v1.firewall',
      'properties': {
          'allowed': [{
              'IPProtocol': 'TCP',
              'ports': [application_port]
          }],
          'sourceRanges': ['0.0.0.0/0']
      }
  }]
  return {'resources': resources}
