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
"""Creates a single project with specified service accounts and APIs enabled."""


def GenerateConfig(context):
  """Generates config."""

  project_id = context.env['name']
  billing_name = 'billing_' + project_id

  resources = [{
      'name': project_id,
      'type': 'cloudresourcemanager.v1.project',
      'properties': {
          'projectId': project_id,
          'parent': {
              'type': 'organization',
              'id': context.properties['organization-id']
          }
      },
      'accessControl': {
          'gcpIamPolicy': context.properties['iam-policy']
      }
  }, {
      'name': billing_name,
      'type': 'deploymentmanager.v2.virtual.projectBillingInfo',
      'metadata': {
          'dependsOn': [project_id]
      },
      'properties': {
          'name': 'projects/' + project_id,
          'billingAccountName': context.properties['billing-account-name']
      }
  }, {
      'name': 'apis',
      'type': 'apis.py',
      'properties': {
          'project': project_id,
          'billing': billing_name,
          'apis': context.properties['apis']
      }
  }, {
      'name': 'service-accounts',
      'type': 'service-accounts.py',
      'properties': {
          'project': project_id,
          'service-accounts': context.properties['service-accounts']
      }
  }]
  if context.properties.get('bucket-export-settings'):
    bucket_name = None
    action_dependency = [project_id]
    if context.properties['bucket-export-settings'].get('create-bucket'):
      bucket_name = project_id + '-export-bucket'
      resources.append({
          'name': bucket_name,
          'type': 'gcp-types/storage-v1:buckets',
          'properties': {
              'project': project_id,
              'name': bucket_name
          },
          'metadata': {
              'dependsOn': [project_id]
          }
      })
      action_dependency.append(bucket_name)
    else:
      bucket_name = context.properties['bucket-export-settings']['bucket-name']
    resources.append({
        'name': 'set-export-bucket',
        'action': 'gcp-types/compute-v1:compute.projects.setUsageExportBucket',
        'properties': {
            'project': project_id,
            'bucketName': 'gs://' + bucket_name
        },
        'metadata': {
            'dependsOn': action_dependency
        }
    })

  return {'resources': resources}
