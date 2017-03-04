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
"""Enables APIs on a specified project."""


def GenerateConfig(context):
  """Generates config."""

  project_id = context.properties['project']
  billing = context.properties['billing']

  resources = []
  for api in context.properties['apis']:
    resources.append({
        'name': project_id + '-' + api,
        'type': 'deploymentmanager.v2.virtual.enableService',
        'metadata': {
            'dependsOn': [project_id, billing]
        },
        'properties': {
            'consumerId': 'project:' + project_id,
            'serviceName': api
        }
    })

  return {'resources': resources}
