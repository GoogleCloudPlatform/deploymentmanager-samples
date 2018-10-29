# Copyright 2017 Google Inc. All rights reserved.
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
""" This template creates an App Engine App resource. """


def generate_config(context):
    """ Generate the deployment configuration. """

    resources = []
    name = context.env['name']

    properties = {
        'id': context.env['project']
    }

    optional_props = [
        'locationId',
        'servingStatus',
        'authDomain',
        'featureSettings'
    ]

    for prop_name in optional_props:
        if prop_name in context.properties:
            properties[prop_name] = context.properties[prop_name]

    resources = [
        {
            'name': name,
            'type': 'gcp-types/appengine-v1:appengine.apps.create',
            'properties': properties
        }
    ]

    outputs = [
        {
            'name': 'name',
            'value': '$(ref.{}.name)'.format(name)
        },
        {
            'name': 'codeBucket',
            'value': '$(ref.{}.codeBucket)'.format(name)
        },
        {
            'name': 'defaultBucket',
            'value': '$(ref.{}.defaultBucket)'.format(name)
        },
        {
            'name': 'defaultHostname',
            'value': '$(ref.{}.defaultHostname)'.format(name)
        },
        {
            'name': 'gcrDomain',
            'value': '$(ref.{}.gcrDomain)'.format(name)
        }
    ]

    return {'resources': resources, 'outputs': outputs}
