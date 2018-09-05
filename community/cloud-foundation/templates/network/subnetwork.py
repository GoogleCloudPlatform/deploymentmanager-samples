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
""" This template creates a subnetwork. """


def generate_config(context):
    """ Entry point for the deployment resources. """

    name = context.properties.get('name') or context.env['name']
    required_properties = ['network', 'ipCidrRange', 'region']
    optional_properties = [
        'enableFlowLogs',
        'privateIpGoogleAccess',
        'secondaryIpRanges'
    ]

    # Load the mandatory properties, then the optional ones (if specifiedP).
    properties = {p: context.properties[p] for p in required_properties}
    properties.update(
        {
            p: context.properties[p]
            for p in optional_properties
            if p in context.properties
        }
    )

    resources = [
        {
            'type': 'compute.v1.subnetwork',
            'name': name,
            'properties': properties
        }
    ]

    return {'resources': resources}
