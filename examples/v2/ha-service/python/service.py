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

"""Creates autoscaled IGM running specified docker image."""


def GenerateConfig(context):
  """Generate YAML resource configuration."""

  name = context.env['name']
  port = context.properties['port']
  target_pool = context.properties['targetPool']
  zone = context.properties['zone']

  igm_name = name + '-igm'
  it_name = name

  it = {
      'name': it_name,
      'type': 'container_instance_template.py',
      'properties': {
          'containerImage': context.properties['containerImage'],
          'dockerEnv': context.properties['dockerEnv'],
          'dockerImage': context.properties['dockerImage'],
          'port': port
      }
  }

  igm = {
      'name': igm_name,
      'type': 'compute.v1.instanceGroupManager',
      'properties': {
          'baseInstanceName': name + '-instance',
          'instanceTemplate': '$(ref.' + it_name + '.instanceTemplateSelfLink)',
          'targetSize': context.properties['minSize'],
          'zone': zone
      }
  }

  # Set target pool if one was provided.
  if target_pool:
    igm['properties']['targetPools'] = ['$(ref.' + target_pool + '.selfLink)']

  autoscaler = {
      'name': name + '-as',
      'type': 'compute.v1.autoscaler',
      'properties': {
          'autoscalingPolicy': {
              'minNumReplicas': context.properties['minSize'],
              'maxNumReplicas': context.properties['maxSize']
          },
          'target': '$(ref.' + igm_name + '.selfLink)',
          'zone': zone
      }
  }

  return {
      'resources': [
          it,
          igm,
          autoscaler
      ],
      'outputs': [{
          'name': 'group',
          'value': '$(ref.' + igm_name + '.instanceGroup)'
      }]
  }
