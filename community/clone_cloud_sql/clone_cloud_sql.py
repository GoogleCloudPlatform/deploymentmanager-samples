# Copyright 2018 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Clones and optionally acquires a Cloud SQL instance."""

def GenerateConfig(ctx):
  resources = []

  # First generate an action to clone the DB.
  clone_properties = {}

  # If a project is specified, then use it. Otherwise act in the project that
  # the deployment is in.
  if 'project' in ctx.properties:
    clone_properties['project'] = ctx.properties['project']
  else:
    clone_properties['project'] = ctx.env['project']
  clone_properties['instance'] = ctx.properties['instanceToClone']
  clone_properties['destinationInstanceName'] = ctx.env['name']
  if 'binLogCoordinates' in ctx.properties:
    clone_properties['binLogCoordinates'] = ctx.properties['binLogCoordinates']
  resources.append({
      'name': 'clone-to-%s' % ctx.env['name'],
      'action': 'gcp-types/sqladmin-v1beta4:sql.instances.clone',
      'properties': clone_properties,
      'metadata': {
          'runtimePolicy': 'CREATE'
      }
  })

  # Optionally, 'acquire' the cloned DB.
  if ctx.properties['acquireClonedDb']:
    resources.append({
        'name': ctx.env['name'],
        'type': 'gcp-types/sqladmin-v1beta4:instances',
        'properties': ctx.properties['acquireProperties']
    })

  return { 'resources': resources }

