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
  replica_name = deployment_name + '-replica'  
  database_name = deployment_name + '-db'

  resources = [{
      'name': instance_name,
      'type': 'gcp-types/sqladmin-v1beta4:instances',
      'properties': {
          'settings': {
              'tier': context.properties['tier'],
              'backupConfiguration' : {
                 'binaryLogEnabled': True,
                 'enabled': True
              }
          }
      }
  }, {
      'name': database_name,
      'type': 'gcp-types/sqladmin-v1beta4:databases',
      'properties': {
          'name': database_name,
          'instance': ''.join(['$(ref.', instance_name,'.name)']),
          'charset': 'utf8'
      }
  }, {
      'name': 'delete-user-root',
      'action': 'gcp-types/sqladmin-v1beta4:sql.users.delete',
      'metadata': {
          'runtimePolicy': ['CREATE'],
          'dependsOn': [ database_name ]          
      },
      'properties': {
          'project': context.env['project'],
          'instance': ''.join(['$(ref.', instance_name,'.name)']),
          'name': 'root',
          'host': '%'
      }
  }, {
      'name': ''.join(['add-user-',context.properties['username']]),
      'action': 'gcp-types/sqladmin-v1beta4:sql.users.insert',
      'metadata': {
          'runtimePolicy': ['CREATE'],
          'dependsOn': [ 'delete-user-root', database_name ]
      },
      'properties': {
          'project': context.env['project'],
          'instance': ''.join(['$(ref.', instance_name,'.name)']),
          'name': context.properties['username'],
          'host': context.properties['host'],
          'password': context.properties['password']
      }
  }]

  for n in range(0,context.properties['readReplicas']):
    resources.append({'name': ''.join([replica_name,'-',str(n)]),
                      'type': 'gcp-types/sqladmin-v1beta4:instances',
                      'metadata': {
                         'dependsOn': [ database_name, ''.join(['add-user-',context.properties['username']]) ]
                      },                      
                      'properties': {
                          'region': context.properties['region'],
                          'masterInstanceName': ''.join(['$(ref.', instance_name,'.name)']),
                          'settings': {
                              'tier': context.properties['tier'],
                              'replicationType': context.properties['replicationType']
                           }
                       } 
                    }) 
  return { 'resources': resources }
