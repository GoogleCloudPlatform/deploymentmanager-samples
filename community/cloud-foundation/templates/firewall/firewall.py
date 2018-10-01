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
""" This template creates firewall rules for a network. """


def generate_config(context):
    """ Entry point for the deployment resources. """

    project = context.env['project']
    network = context.properties.get('network')

    resources = []
    for i, rule in enumerate(context.properties['rules'], 1000):
        # Use VPC if specified in the properties. Otherwise, specify
        # the network URL in the config. If the network is not specified in
        # the config, the API defaults to 'global/networks/default'.
        if network and not rule.get('network'):
            rule['network'] = 'projects/{}/global/networks/{}'.format(
                project,
                network
            )
        rule['priority'] = rule.get('priority', i)
        resources.append(
            {
                'name': rule['name'],
                'type': 'compute.beta.firewall',
                'properties': rule
            }
        )
    return {'resources': resources}
