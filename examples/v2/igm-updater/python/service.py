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

"""Creates autoscaled, network LB IGM running specified VM image.

If necessary, create a second Instance Template and an Updater.
"""


def GenerateConfig(context):
  """Generate YAML resource configuration."""

  name = context.env['name']
  igm_name = name + '-igm'
  curr_it_name = name + '-it-' + context.properties['currVersion']['name']
  machine_type = context.properties['machineType']
  zone = context.properties['zone']

  config = {'resources': []}

  # The instance template.
  current_it = {
      'name': curr_it_name,
      'type': 'instance-template.py',
      'properties': {
          'machineType': machine_type,
          'zone': zone,
          'itName': curr_it_name,
          'image': context.properties['currVersion']['image']
      }
  }
  config['resources'].append(current_it)

  # The instance group manager.
  igm = {
      'name': igm_name,
      'type': 'compute.beta.instanceGroupManager',
      'properties': {
          'baseInstanceName': igm_name + '-instance',
          'instanceTemplate': '$(ref.' + curr_it_name + '.selfLink)',
          'zone': zone,
          'targetSize': 1,
          'targetPools': [
              '$(ref.' + context.properties['targetPool'] + '.selfLink)',
          ],
          'updatePolicy': {
              'minimalAction': 'REPLACE',
              'type': 'PROACTIVE',
          }
      }
  }
  config['resources'].append(igm)

  # The autoscaler.
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
  config['resources'].append(autoscaler)

  return config
