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
"""Creates a Cloud Router and  VPN Tunnel."""


def generate_config(context):
    """ Entry point for the deployment resources """

    resources = [
        {
            'name': context.env['name'],
            'type': 'compute.v1.router',
            'properties':
                {
                    'name':
                        context.properties['name'],
                    'bgp': {
                        'asn': context.properties['asn']
                    },
                    'network':
                        generate_network_url(
                            context,
                            context.properties['network']
                        ),
                    'region':
                        context.properties['region']
                }
        }
    ]

    return {
        'resources':
            resources,
        'outputs':
            [
                {
                    'name': 'routerUrl',
                    'value': '$(ref.' + context.env['name'] + '.selfLink)'
                }
            ]
    }


def generate_network_url(context, network):

    return 'projects/{}/global/networks/{}'.format(
        context.env['project'],
        network
    )