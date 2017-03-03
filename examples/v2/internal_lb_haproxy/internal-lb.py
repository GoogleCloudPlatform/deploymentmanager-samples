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

"""Creates a load balancer using HAProxy."""


def GenerateConfig(context):
  """Generate configuration."""

  lb_name = ''.join([context.env['deployment'],
                     '-',
                     context.env['name'],
                     '-internal-lb'])

  metadata = {
      'algorithm': context.properties['algorithm'],
      'app-port': context.properties['app-port'],
      'port': context.properties['port'],
      'groups': ' '.join(context.properties['groups'])
  }

  resources = [{
      'name': lb_name,
      'type': 'instance.py',
      'properties': {
          'machine-type': context.properties['machine-type'],
          'metadata': metadata,
          'metadata-from-file': {
              'startup-script': 'haproxy-startup-script.sh'
          },
          'zone': context.properties['zone']
      }
  }]

  return {
      'resources': resources,
      'outputs': [{
          'name': 'address',
          'value': '$(ref.' + lb_name + '.address)'
      }]
  }

