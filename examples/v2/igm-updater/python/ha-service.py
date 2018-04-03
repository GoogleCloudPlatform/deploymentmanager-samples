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

"""Creates an HA service configuration."""


def GenerateConfig(context):
  """Generates config."""

  lb_name = context.env['deployment'] + '-lb'
  region = context.properties['zones'][0]['zone'][:-2]

  config = {'resources': []}

  # A zonal service.py resource for each zone in the properties list.
  for deploy_zone in context.properties['zones']:
    zone_name = deploy_zone['zone']

    properties = {
        'currVersion': deploy_zone['curr'],
        'targetPool': lb_name + '-tp',
        'minSize': context.properties['minSize'],
        'maxSize': context.properties['maxSize'],
        'machineType': context.properties['machineType'],
        'zone': zone_name
    }

    service = {
        'name': context.env['deployment'] + '-service-' + zone_name,
        'type': 'service.py',
        'properties': properties
    }

    config['resources'].append(service)

  # A L3 load balancer setup for the HA service.
  lb = {
      'name': lb_name,
      'type': 'lb-l3.py',
      'properties': {
          'port': 8080,
          'region': region
      }
  }

  config['resources'].append(lb)

  return config

