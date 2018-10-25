# Copyright 2018 Google Inc. All rights reserved.
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
""" This template creates an Instance Template. """


def generate_config(context):
    """ Entry point for the deployment resources. """

    properties = context.properties
    name = properties.get('name', context.env['name'])
    target_size = properties.get('targetSize')
    base_name = properties.get('baseInstanceName')
    instance_template_name = properties.get('instanceTemplate')
    zone = properties.get('zone')
    managed_instance_group_template = {
        'name': name,
        'type': 'compute.v1.instanceGroupManager',
        'properties':
            {
                'zone': zone,
                'targetSize': target_size,
                'baseInstanceName': base_name,
                'instanceTemplate': instance_template_name
            }
    }

    return {
        'resources': [managed_instance_group_template],
        'outputs':
            [
                {
                    'name': 'name',
                    'value': name
                },
                {
                    'name': 'selfLink',
                    'value': '$(ref.{}.selfLink)'.format(name)
                }
            ]
    }
