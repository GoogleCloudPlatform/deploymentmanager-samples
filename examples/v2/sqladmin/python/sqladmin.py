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
"""Creates a Cloud SQL instance and database."""

import json


def GenerateConfig(context):
  """Generate YAML resource configuration."""
  deployment_name = context.env['deployment']
  instance_name = deployment_name + '-instance'
  database_name = deployment_name + '-db'

  resources = [{
      'name': instance_name,
      'type': 'gcp-types/sqladmin-v1beta4:instances',
      'properties': {
          'settings': {
              'tier': context.properties['tier']
          }
      }
  }, {
      'name': database_name,
      'type': 'gcp-types/sqladmin-v1beta4:databases',
      'metadata': {
          'dependsOn': [instance_name]
      },
      'properties': {
          'name': database_name,
          'instance': instance_name,
          'charset': 'utf8'
      }
  }]
  return { 'resources': resources }
