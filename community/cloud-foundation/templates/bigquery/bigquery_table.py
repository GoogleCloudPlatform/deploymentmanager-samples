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
"""Creates a BigQuery Dataset."""


def generate_config(context):
    """ Entry point for the deployment resources """

    name = context.properties['name']

    properties = {
        'tableReference':
            {
                'tableId': name,
                'datasetId': context.properties['datasetId'],
                'projectId': context.env['project']
            },
        'datasetId': context.properties['datasetId']
    }

    if context.properties.get('description'):
        properties['description'] = context.properties['description']

    if context.properties.get('friendlyName'):
        properties['friendlyName'] = context.properties['friendlyName']

    if context.properties.get('expirationTime'):
        properties['expirationTime'] = context.properties['expirationTime']

    if context.properties.get('labels'):
        properties['labels'] = context.properties['labels']

    if context.properties.get('schema'):
        properties['schema'] = context.properties['schema']

    if context.properties.get('timePartitioning'):
        properties['timePartitioning'] = context.properties['timePartitioning']

    if context.properties.get('view'):
        properties['view'] = context.properties['view']

    resources = [
        {
            'type': 'bigquery.v2.table',
            'name': name,
            'properties': properties,
            'metadata': {
                'dependsOn': [context.properties['datasetId']]
            }
        }
    ]

    outputs = [
        {
            'name': 'selfLink',
            'value': '$(ref.{}.selfLink)'.format(name)
        },
        {
            'name': 'etag',
            'value': '$(ref.{}.etag)'.format(name)
        },
        {
            'name': 'creationTime',
            'value': '$(ref.{}.creationTime)'.format(name)
        },
        {
            'name': 'lastModifiedTime',
            'value': '$(ref.{}.lastModifiedTime)'.format(name)
        },
        {
            'name': 'location',
            'value': '$(ref.{}.location)'.format(name)
        },
        {
            'name': 'numBytes',
            'value': '$(ref.{}.numBytes)'.format(name)
        },
        {
            'name': 'numLongTermBytes',
            'value': '$(ref.{}.numLongTermBytes)'.format(name)
        },
        {
            'name': 'numRows',
            'value': '$(ref.{}.numRows)'.format(name)
        },
        {
            'name': 'type',
            'value': '$(ref.{}.type)'.format(name)
        }
    ]

    return {'resources': resources, 'outputs': outputs}
