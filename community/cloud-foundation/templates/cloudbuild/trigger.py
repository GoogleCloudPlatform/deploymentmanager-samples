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
""" This template creates a Cloud Build trigger. """


def generate_config(context):
    """ Entry point for the deployment resources. """

    resources = []
    properties = context.properties
    name = context.env['name']
    trigger_template = properties['triggerTemplate']
    build_def = properties.get('build')
    build_filename = properties.get('filename')
    build_trigger = {
        'name':
            name,
        'action':
            'gcp-types/cloudbuild-v1:cloudbuild.projects.triggers.create',
        'properties': {
            'triggerTemplate': trigger_template
        }
    }

    optional_properties = [
        'description',
        'disabled',
        'substitutions',
        'ignoredFiles',
        'includedFiles'
    ]

    for prop in optional_properties:
        if prop in properties:
            build_trigger['properties'][prop] = properties[prop]

    if build_def:
        build_trigger['properties']['build'] = build_def
    elif build_filename:
        build_trigger['properties']['filename'] = build_filename

    resources.append(build_trigger)

    # Output variables
    outputs = [
        {
            'name': 'id',
            'value': '$(ref.{}.id)'.format(name)
        },
        {
            'name': 'createTime',
            'value': '$(ref.{}.createTime)'.format(name)
        }
    ]

    return {'resources': resources, 'outputs': outputs}
