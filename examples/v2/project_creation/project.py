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

import copy
import sys
from apis import ApiResourceName

def GenerateConfig(context):
  """Generates config."""

  project_id = context.env['name']
  billing_name = 'billing_' + project_id

  if not IsProjectParentValid(context.properties):
    sys.exit(('Invalid [organization-id, parent-folder-id], '
              'must specify exactly one.'))

  parent_type = ''
  parent_id = ''

  if 'organization-id' in context.properties:
    parent_type = 'organization'
    parent_id = context.properties['organization-id']
  else:
    parent_type = 'folder'
    parent_id = context.properties['parent-folder-id']

  resources = [{
      'name': project_id,
      'type': 'cloudresourcemanager.v1.project',
      'properties': {
          'name': project_id,
          'projectId': project_id,
          'parent': {
              'type': parent_type,
              'id': parent_id
          }
      },
      'accessControl': {
          'gcpIamPolicy':
              MergeCallingServiceAccountWithOwnerPermissinsIntoBindings(
                  context.env, context.properties)
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
          'apis': context.properties['apis'],
          'concurrent_api_activation':
              context.properties['concurrent_api_activation']
      }
  }, {
      'name': 'service-accounts',
      'type': 'service-accounts.py',
      'properties': {
          'project': project_id,
          'service-accounts': context.properties['service-accounts']
      }
  }]
  if context.properties.get('set-dm-service-account-as-owner'):
      # The name needs to be different in every update
      # due to a known issue in DM.
      get_iam_policy_name = 'get-iam-policy'
      resources.extend([{
          'name': get_iam_policy_name,
          'action': 'gcp-types/cloudresourcemanager-v1:cloudresourcemanager.projects.getIamPolicy',
          'properties': {
            'resource': project_id,
          },
          'metadata': {
            'dependsOn': [ApiResourceName(
                project_id, 'deploymentmanager.googleapis.com')],
            'runtimePolicy': ['UPDATE_ALWAYS']
          }
      }, {
       # Add the service account that deployment manager will use in this project
       # as owner so it can set IAM policies on resources
          'name': 'patch-iam-policy',
          'action': 'gcp-types/cloudresourcemanager-v1:cloudresourcemanager.projects.setIamPolicy',
          'properties': {
            'resource': project_id,
            'policy': '$(ref.' + get_iam_policy_name + ')',
            'gcpIamPolicyPatch': {
               'add': [{
                 'role': 'roles/owner',
                 'members': [
                   'serviceAccount:$(ref.' + project_id + '.projectNumber)@cloudservices.gserviceaccount.com'
                 ]
               }]
             }
          }
      }])
  if context.properties.get('bucket-export-settings'):
    bucket_name = None
    action_dependency = [project_id,
                         ApiResourceName(project_id, 'compute.googleapis.com')]
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
              'dependsOn': [project_id,
                            ApiResourceName(
                                project_id, 'storage-component.googleapis.com')]
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

def MergeCallingServiceAccountWithOwnerPermissinsIntoBindings(env, properties):
  """ A helper function that merges the acting service account of the project
      creator as an owner of the project being created
  """
  service_account = ('serviceAccount:{0}@cloudservices.gserviceaccount.com'
                     .format(env['project_number']))
  set_creator_sa_as_owner = {
      'role': 'roles/owner',
      'members': [
          service_account,
      ]
  }
  if 'iam-policy' not in properties:
    return {
        'bindings': [
            set_creator_sa_as_owner,
        ]
    }

  iam_policy = copy.deepcopy(properties['iam-policy'])
  bindings = []
  if 'bindings' in iam_policy:
    bindings = iam_policy['bindings']
  else:
    iam_policy['bindings'] = bindings

  merged = False
  for binding in bindings:
    if binding['role'] == 'roles/owner':
      merged = True
      if service_account not in binding['members']:
        binding['members'].append(service_account)
      break

  if not merged:
    bindings.append(set_creator_sa_as_owner)

  return iam_policy

def IsProjectParentValid(properties):
  """ A helper function to validate that the project is either under a folder
      or under an organization and not both
  """
  if ('organization-id' not in properties and
      'parent-folder-id' not in properties):
    return False
  if 'organization-id' in properties and 'parent-folder-id' in properties:
    return False
  return True
