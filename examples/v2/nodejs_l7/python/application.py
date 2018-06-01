
# Copyright 2016 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Create appplication template with back-end and front-end templates."""


def GenerateConfig(context):
  """Generate configuration."""

  backend = context.env['deployment'] + '-backend'
  frontend = context.env['deployment'] + '-frontend'
  static_service = context.env['deployment'] + '-static-service'
  application = context.env['deployment'] + '-application'

  container_image = 'family/cos-stable'

  application_port = 8080
  lb_port = 8080
  mysql_port = 8080

  resources = [{
      'name': backend,
      'type': 'container_vm.py',
      'properties': {
          'zone': context.properties['primaryZone'],
          'dockerImage': context.properties['backendImage'],
          'containerImage': container_image,
          'port': mysql_port
      }
  }, {
      'name': frontend,
      'type': 'service.py',
      'properties': {
          'primaryZone': context.properties['primaryZone'],
          'primarySize': 2,
          'secondaryZone': context.properties['secondaryZone'],
          'secondarySize': 0,
          'dockerImage': context.properties['frontendImage'],
          'containerImage': container_image,
          'port': application_port,
          'service': 'http',
          # If left out will default to 1
          'maxSize': 20,
          # Define the variables that are exposed to container as env variables.
          'dockerEnv': {
              'SEVEN_SERVICE_MYSQL_PORT': mysql_port,
              'SEVEN_SERVICE_PROXY_HOST': '$(ref.' + backend
                                          + '.networkInterfaces[0].networkIP)'
          }
      }
  }, {
      'name': static_service,
      'type': 'service.py',
      'properties': {
          'primaryZone': context.properties['primaryZone'],
          'primarySize': 2,
          'secondaryZone': context.properties['secondaryZone'],
          'secondarySize': 0,
          'dockerImage': context.properties['staticImage'],
          'containerImage': container_image,
          'port': application_port,
          'service': 'httpstatic',
          # If left out will default to 1
          'maxSize': 20
      }
  }, {
      'name': application + '-urlmap',
      'type': 'compute.v1.urlMap',
      'properties': {
          'defaultService': '$(ref.' + frontend + '-bes.selfLink)',
          'hostRules': [{
              'hosts': ['*'],
              'pathMatcher': 'pathmap'
          }],
          'pathMatchers': [{
              'name': 'pathmap',
              'defaultService': '$(ref.' + frontend + '-bes.selfLink)',
              'pathRules': [{
                  'paths': ['/static', '/static/*'],
                  'service': '$(ref.' + static_service + '-bes.selfLink)'
              }]
          }]
      }
  }, {
      'name': application + '-targetproxy',
      'type': 'compute.v1.targetHttpProxy',
      'properties': {
          'urlMap': '$(ref.' + application + '-urlmap.selfLink)'
      }
  }, {
      'name': application + '-l7lb',
      'type': 'compute.v1.globalForwardingRule',
      'properties': {
          'IPProtocol': 'TCP',
          'portRange': lb_port,
          'target': '$(ref.' + application + '-targetproxy.selfLink)'
      }
  }, {
      'name': application + '-fw',
      'type': 'compute.v1.firewall',
      'properties': {
          'allowed': [{
              'IPProtocol': 'TCP',
              'ports': [lb_port]
          }],
          'sourceRanges': ['0.0.0.0/0']
      }
  }]
  return {'resources': resources}
