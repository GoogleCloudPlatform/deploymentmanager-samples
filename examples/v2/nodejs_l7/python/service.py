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

"""Creates primary/secondary zone autoscaled IGM running specified container."""


def GenerateConfig(context):
  """Generate YAML resource configuration."""

  name = context.env['name']

  resources = [{
      'name': name,
      'type': 'container_instance_template.py',
      'properties': {
          'port': context.properties['port'],
          'dockerEnv': context.properties['dockerEnv'],
          'dockerImage': context.properties['dockerImage'],
          'containerImage': context.properties['containerImage']
      }
  }, {
      'name': name + '-pri',
      'type': 'autoscaled_group.py',
      'properties': {
          'zone': context.properties['primaryZone'],
          'size': context.properties['primarySize'],
          'maxSize': context.properties['maxSize'],
          'port': context.properties['port'],
          'service': context.properties['service'],
          'baseInstanceName': name + '-instance',
          'instanceTemplate': '$(ref.' + name + '-it.selfLink)'
      }
  }, {
      'name': name + '-sec',
      'type': 'autoscaled_group.py',
      'properties': {
          'zone': context.properties['secondaryZone'],
          'size': context.properties['secondarySize'],
          'maxSize': context.properties['maxSize'],
          'port': context.properties['port'],
          'service': context.properties['service'],
          'baseInstanceName': name + '-instance',
          'instanceTemplate': '$(ref.' + name + '-it.selfLink)'
      }
  }, {
      'name': name + '-hc',
      'type': 'compute.v1.httpHealthCheck',
      'properties': {
          'port': context.properties['port'],
          'requestPath': '/_ah/health'
      }
  }, {
      'name': name + '-bes',
      'type': 'compute.v1.backendService',
      'properties': {
          'port': context.properties['port'],
          'portName': context.properties['service'],
          'backends': [{
              'name': name + '-primary',
              'group': '$(ref.' + name + '-pri-igm.instanceGroup)'
          }, {
              'name': name + '-secondary',
              'group': '$(ref.' + name + '-sec-igm.instanceGroup)'
          }],
          'healthChecks': ['$(ref.' + name + '-hc.selfLink)']
      }
  }]
  return {'resources': resources}
