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

  if 'prevVersion' in context.properties:
    # If performing an instance group update we a need instance template and an
    # updater resource.
    prev_it_name = name + '-it-' + context.properties['prevVersion']['name']
    new_it = {
        'name': prev_it_name,
        'type': 'instance-template.py',
        'properties': {
            'machineType': machine_type,
            'zone': zone,
            'itName': prev_it_name,
            'image': context.properties['prevVersion']['image']
        }
    }
    config['resources'].append(new_it)

    updater = {
        'name': curr_it_name + '-igupdater',
        'type': 'replicapoolupdater.v1beta1.rollingUpdate',
        'properties': {
            'zone': zone,
            'instanceGroupManager': '$(ref.' +  igm_name + '.selfLink)',
            'actionType': 'RECREATE',
            'instanceTemplate': '$(ref.' + curr_it_name + '.selfLink)'
        }
    }
    config['resources'].append(updater)

  # The instance group manager.
  igm = {
      'name': igm_name,
      'type': 'compute.v1.instanceGroupManager',
      'properties': {
          'baseInstanceName': igm_name + '-instance',
          'instanceTemplate': '$(ref.' + curr_it_name + '.selfLink)',
          'zone': zone,
          'targetSize': 1
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
