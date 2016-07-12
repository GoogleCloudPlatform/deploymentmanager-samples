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

"""Creates autoscaled, network LB IGM running specified docker image."""

# Defaults
SIZE_KEY = 'size'
DEFAULT_SIZE = 1

MAX_SIZE_KEY = 'maxSize'
DEFAULT_MAX_SIZE = 1

CONTAINER_IMAGE_KEY = 'containerImage'
DEFAULT_CONTAINER_IMAGE = 'container-vm-v20160217'

DOCKER_ENV_KEY = 'dockerEnv'
DEFAULT_DOCKER_ENV = '{}'


def GenerateConfig(context):
  """Generate YAML resource configuration."""

  # Set up some defaults if the user didn't provide any
  if SIZE_KEY not in context.properties:
    context.properties[SIZE_KEY] = DEFAULT_SIZE
  if MAX_SIZE_KEY not in context.properties:
    context.properties[MAX_SIZE_KEY] = DEFAULT_MAX_SIZE
  if CONTAINER_IMAGE_KEY not in context.properties:
    context.properties[CONTAINER_IMAGE_KEY] = DEFAULT_CONTAINER_IMAGE
  if DOCKER_ENV_KEY not in context.properties:
    context.properties[DOCKER_ENV_KEY] = DEFAULT_DOCKER_ENV

  # Pull the region out of the zone
  region = context.properties['zone'][:context.properties['zone'].rfind('-')]
  name = context.env['name']

  resources = [{
      'name': name,
      'type': 'container_instance_template.py',
      'properties': {
          'port': context.properties['port'],
          'dockerEnv': context.properties[DOCKER_ENV_KEY],
          'dockerImage': context.properties['dockerImage'],
          'containerImage': context.properties[CONTAINER_IMAGE_KEY]
      }
  }, {
      'name': name + '-igm',
      'type': 'compute.v1.instanceGroupManager',
      'properties': {
          'zone': context.properties['zone'],
          'targetSize': context.properties[SIZE_KEY],
          'targetPools': ['$(ref.' + name + '-tp.selfLink)'],
          'baseInstanceName': name + '-instance',
          'instanceTemplate': '$(ref.' + name + '-it.selfLink)'
      }
  }, {
      'name': name + '-as',
      'type': 'compute.v1.autoscaler',
      'properties': {
          'zone': context.properties['zone'],
          'target': '$(ref.' + name + '-igm.selfLink)',
          'autoscalingPolicy': {
              'maxNumReplicas': context.properties[MAX_SIZE_KEY]
          }
      }
  }, {
      'name': name + '-hc',
      'type': 'compute.v1.httpHealthCheck',
      'properties': {
          'port': context.properties['port'],
          'requestPath': '/_ah/health'
      }
  }, {
      'name': name + '-tp',
      'type': 'compute.v1.targetPool',
      'properties': {
          'region': region,
          'healthChecks': ['$(ref.' + name + '-hc.selfLink)']
      }
  }, {
      'name': name + '-lb',
      'type': 'compute.v1.forwardingRule',
      'properties': {
          'region': region,
          'portRange': context.properties['port'],
          'target': '$(ref.' + name + '-tp.selfLink)'
      }
  }]
  return {'resources': resources}
