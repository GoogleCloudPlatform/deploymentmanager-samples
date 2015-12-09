# Copyright 2015 Google Inc. All rights reserved.
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
DEFAULT_CONTAINER_IMAGE = 'container-vm-v20151103'

DOCKER_ENV_KEY = 'dockerEnv'
DEFAULT_DOCKER_ENV = {}


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

  name = context.env['name']
  port = context.properties['port']
  target_pool = context.properties['targetPool']
  zone = context.properties['zone']

  igm_name = name + '-igm'
  it_name = name + '-it'

  resources = [{
      'name': it_name,
      'type': 'container_instance_template.py',
      'properties': {
          CONTAINER_IMAGE_KEY: context.properties[CONTAINER_IMAGE_KEY],
          DOCKER_ENV_KEY: context.properties[DOCKER_ENV_KEY],
          'dockerImage': context.properties['dockerImage'],
          'port': port
      }
  }, {
      'name': igm_name,
      'type': 'compute.v1.instanceGroupManager',
      'properties': {
          'baseInstanceName': name + '-instance',
          'instanceTemplate': '$(ref.' + it_name + '.selfLink)',
          'targetSize': context.properties[SIZE_KEY],
          'targetPools': ['$(ref.' + target_pool + '.selfLink)'],
          'zone': zone
      }
  }, {
      'name': name + '-as',
      'type': 'compute.v1.autoscaler',
      'properties': {
          'autoscalingPolicy': {
              'maxNumReplicas': context.properties[MAX_SIZE_KEY]
          },
          'target': '$(ref.' + igm_name + '.selfLink)',
          'zone': zone
      }
  }]

  return {'resources': resources}

