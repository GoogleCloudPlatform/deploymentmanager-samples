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
"""Creates a cloud Bigtable instance, cluster, and table."""

import copy


def _ClusterProperties(cluster, project_path):
  cluster['location'] = project_path + '/locations/' + cluster['location']
  return cluster


def GenerateConfig(context):
  """Generate YAML resource configuration."""
  deployment_name = context.env['deployment']
  instance_name = context.properties['instanceId']
  if 'projectId' in context.properties:
    project_id = context.properties['projectId']
  else:
    project_id = context.env['project']
  project_path = 'projects/' + project_id
  clusters = []
  for id, properties in context.properties['clusters'].iteritems():
    clusters.append({
        'id': id,
        'properties': _ClusterProperties(properties, project_path)
    })
  initial_cluster = {}
  for cluster in clusters:
    initial_cluster[cluster['id']] = cluster['properties']
  instance_create = {
      'name':
          'instance_create',
      'action':
          'gcp-types/bigtableadmin-v2:bigtableadmin.projects.instances.create',
      'properties': {
          'parent': project_path,
          'instanceId': instance_name,
          'clusters': copy.deepcopy(initial_cluster),
          'instance': context.properties['instance']
      },
      'metadata': {
          'runtimePolicy': ['CREATE']
      }
  }
  instance_update = {
      'name':
          'instance_update',
      'action':
          'gcp-types/bigtableadmin-v2:bigtableadmin.projects.instances.update',
      'properties': copy.deepcopy(context.properties['instance']),
      'metadata': {
          'runtimePolicy': ['UPDATE_ON_CHANGE']
      }
  }
  instance_update['properties']['name'] = '$(ref.' + instance_create['name'] + '.name)'
  instance_id = '$(ref.' + instance_create['name'] + '.name)'
  instance_delete = {
      'name':
          'instance_delete',
      'action':
          'gcp-types/bigtableadmin-v2:bigtableadmin.projects.instances.delete',
      'properties': {
          'name': instance_id
      },
      'metadata': {
          'runtimePolicy': ['DELETE'],
          'dependsOn': []
      }
  }
  resources = [instance_create, instance_update, instance_delete]
  if context.properties['instance']['type'] != 'DEVELOPMENT':
    # Updating the clusters only make sense for non development instances
    for cluster in clusters:
      cluster['properties']['name'] = instance_id + '/clusters/' + cluster['id']
      resources.append({
          'name':
              cluster['id'],
          'action':
              'gcp-types/bigtableadmin-v2:bigtableadmin.projects.instances.clusters.update',
          'properties':
              cluster['properties'],
          'metadata': {
              'runtimePolicy': ['UPDATE_ON_CHANGE'],
              'dependsOn': [instance_update['name']]
          }
      })
  for table in context.properties['tables']:
    table_resource = {
      'name': 'table-' + table,
      'type': 'gcp-types/bigtableadmin-v2:projects.instances.tables',
      'properties': {
        'parent': '$(ref.' + instance_create['name'] + '.name)',
        'tableId': table,
        'table': context.properties['tables'][table]
      }
    }
    resources.append(table_resource)
  return {'resources': resources}
