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
"""
This template creates an IP reservation based on the input 
option (External, Internal, or Global)
"""

import copy


def get_deployment_type(ip_type):
    """
    Input: ip_type (internal, regional, or global).
    Output: the correct type for Deployment Manager to consume.
    """

    if ip_type in ['internal', 'regional']:
        return 'compute.v1.address'
    elif ip_type in ['global']:
        return 'compute.v1.globalAddress'
    raise ValueError('Input {} is not an acceptable IP type'.format(ip_type))


def get_resource_type(ip_type):
    """
    Input: ip_type (internal, regional, or global).
    Output: the correct type for Deployment Manager to consume. 
    ??? Looks like eirther this def of the previous one is just a copy of the other one... ??? 
    """

    if ip_type in ['internal']:
        return 'INTERNAL'
    elif ip_type in ['global', 'regional']:
        return 'EXTERNAL'
    raise ValueError('Input {} is not an acceptable IP type'.format(ip_type))


def generate_config(context):
    """
    Input:  The context is an object containing the input configuration for
            Deployment Manager.
    Output: The payload sent to Deployment Manager including resources
            and outputs.
    """

    resources = []
    outputs = []

    for ip in context.properties['ips']:
        resource_type = get_resource_type(ip['ipType'])
        deployment_type = get_deployment_type(ip['ipType'])
        ip_payload = {
            'type': deployment_type,
            'name': ip['name'],
            'properties':
                {
                    'addressType': resource_type,
                    'resourceType': 'addresses',
                    'region': ip.get('region',
                                     ''),
                    'description': ip.get('info',
                                          ''),
                }
        }
        if ip.get('ipAddress'):
            ip_payload['properties']['address'] = ip['ipAddress']
        if ip.get('subnet'):
            ip_payload['properties']['subnetwork'] = ip['subnet']
        resources.append(copy.copy(ip_payload))

        outputs.extend(
            [
                {
                    'name': ip['name'],
                    'value': '$(ref.{}.name)'.format(ip['name'])
                },
                {
                    'name': '{}-ipAddress'.format(ip['name']),
                    'value': '$(ref.{}.address)'.format(ip['name'])
                }
            ]
        )

    return {'resources': resources, 'outputs': outputs}
