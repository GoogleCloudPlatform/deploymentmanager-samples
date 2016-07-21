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


def GenerateConfig(context):
  """Generate YAML resource configuration."""

  # NOTE: Once we can specify the port/service during creation of IGM,
  # we will wire it up here.
  name = context.env['name']
  resources = [{
      'name': name + '-igm',
      'type': 'compute.v1.instanceGroupManager',
      'properties': {
          'zone': context.properties['zone'],
          'targetSize': context.properties['size'],
          'baseInstanceName': name + '-instance',
          'instanceTemplate': context.properties['instanceTemplate']
      }
  }, {
      'name': name + '-as',
      'type': 'compute.v1.autoscaler',
      'properties': {
          'zone': context.properties['zone'],
          'target': '$(ref.' + name + '-igm.selfLink)',
          'autoscalingPolicy': {
              'maxNumReplicas': context.properties['maxSize']

          }
      }
  }]
  return {'resources': resources}
