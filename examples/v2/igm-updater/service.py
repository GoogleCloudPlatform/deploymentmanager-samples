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

"""Creates autoscaled, network LB IGM running specified VM image.

If necessary, create a second Instance Template and an Updater.
"""


def GenerateConfig(context):
  """Generate YAML resource configuration."""

  name = context.env['name']
  igm_name = name + '-igm'
  curr_it_name = name + '-it-' + context.properties['currversion']['name']
  vmmachine = context.properties['vmSize']
  zone = context.properties['zone']

  config = {'resources': []}

  # The instance template.
  currentit = {
      'name': curr_it_name,
      'type': 'instancetemplate.py',
      'properties': {
          'vmmachine': vmmachine,
          'zone': zone,
          'itName': curr_it_name,
          'image': context.properties['currversion']['image']
      }
  }
  config['resources'].append(currentit)

  if 'prevversion' in context.properties:
    # If performing an instance group update we a need instance template and an
    # updater resource.
    prev_it_name = name + '-it-' + context.properties['prevversion']['name']
    newit = {
        'name': prev_it_name,
        'type': 'instancetemplate.py',
        'properties': {
            'vmmachine': vmmachine,
            'zone': zone,
            'itName': prev_it_name,
            'image': context.properties['prevversion']['image']
        }
    }
    config['resources'].append(newit)

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
      'type': 'autoscaler.v1beta2.autoscaler',
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

