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
import hashlib
import random
import re
import sys
from apis import ApiResourceName

def UpdateSharedVPCSettings(context, resources, project_id):
  if context.properties.get('shared_vpc_host'):
     resources.append({
        'name': project_id + '-xpn-host',
        'type': 'compute.beta.xpnHost',
        'properties': {
            'organization-id': context.properties['organization-id'],
            'billing-account-name': context.properties['billing-account-name'],
            'project': project_id,
        },
        'metadata': {
            'dependsOn': [
                ApiResourceName(project_id, 'compute.googleapis.com'),
                project_id,
            ],
        }
     })
  if context.properties.get('shared_vpc_service_of'):
      resources.append({
        'name': project_id + '-xpn-service-' +
            context.properties['shared_vpc_service_of'],
        'type': 'compute.beta.xpnResource',
        'properties': {
            'organization-id': context.properties['organization-id'],
            'billing-account-name': context.properties['billing-account-name'],
            'project': [context.properties['shared_vpc_service_of']],
            'xpnResource': {
                'id': project_id,
                'type': 'PROJECT',
            },
        },
        'metadata': {
            'dependsOn': [
                ApiResourceName(project_id, 'compute.googleapis.com'),
                project_id,
                context.properties['shared_vpc_service_of'] + '-xpn-host',
            ],
        }
      })

def AutoCompleteServiceAccount(policies, project_id):
  pm = re.compile(r'serviceAccount:([a-zA-Z0-9_-]+)$')
  for p in policies:
    for i, m in enumerate(p['members']):
      if pm.match(m):
        groups = pm.match(m).groups()
        sa_name = groups[0] + "@" + project_id + ".iam.gserviceaccount.com"
        print(sa_name) 
        p['members'][i] = "serviceAccount:" + sa_name

def UpdateIAMPolicy(context, resources, project_id):
  if (context.properties.get('iam-policy-patch') or
      context.properties.get('set-dm-service-account-as-owner')):
    iam_policy_patch = context.properties.get('iam-policy-patch', {})
    if iam_policy_patch.get('add'):
      policies_to_add = iam_policy_patch['add']
    else:
      policies_to_add = []
    if iam_policy_patch.get('remove'):
      policies_to_remove = iam_policy_patch['remove']
    else:
      policies_to_remove = []
 
    if context.properties.get('set-dm-service-account-as-owner'):
      svc_acct = 'serviceAccount:{}@cloudservices.gserviceaccount.com'.format(
        '$(ref.{}.projectNumber)'.format(project_id)
      )
 
      # Merge the default DM service account into the owner role if it exists
      owner_idx = [bind['role'] == 'roles/owner' for bind in policies_to_add]
      try:
        # Determine where in policies_to_add the owner role is.
        idx = owner_idx.index(True)
      except ValueError:
        # If the owner role is not defined just append to what to add.
        policies_to_add.append({'role': 'roles/owner', 'members': [svc_acct]})
      else:
        # Append the default DM service account to the owner role members
        if svc_acct not in policies_to_add[idx]['members']:
          policies_to_add[idx]['members'].append(svc_acct)
 
    get_iam_policy_dependencies = [ project_id ]
    for api in context.properties['apis']:
      get_iam_policy_dependencies.append(ApiResourceName(project_id, api))
 
    AutoCompleteServiceAccount(policies_to_add, project_id)
    AutoCompleteServiceAccount(policies_to_remove, project_id)

    resources.extend([{
        # Get the IAM policy first so that we do not remove any existing bindings.
        'name': 'get-iam-policy-' + project_id,
        'action': 'gcp-types/cloudresourcemanager-v1:cloudresourcemanager.projects.getIamPolicy',
        'properties': {
          'resource': project_id,
        },
        'metadata': {
          'dependsOn': get_iam_policy_dependencies,
          'runtimePolicy': ['UPDATE_ALWAYS']
        }
    }, {
        # Set the IAM policy patching the existing policy with what ever is currently in the
        # config.
        'name': 'patch-iam-policy-' + project_id,
        'action': 'gcp-types/cloudresourcemanager-v1:cloudresourcemanager.projects.setIamPolicy',
        'properties': {
          'resource': project_id,
          'policy': '$(ref.get-iam-policy-' + project_id + ')',
          'gcpIamPolicyPatch': {
             'add': policies_to_add,
             'remove': policies_to_remove
          }
        },
        'metadata': {
          'dependsOn': [project_id]
        }
    }])

def GenerateConfig(context):
  """Generates config."""

  project_name = context.env['name']
  project_id = None
  if 'project-id' in context.properties:
    m = hashlib.sha256()
    m.update(project_name.encode())
    salt = "92jc8slt"
    m.update(salt.encode())
    postfix = m.hexdigest()
    project_id = (project_name + "-" + postfix)[:30]
  else:
    project_id = context.properties['project-id']

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
          'name': project_name,
          'projectId': project_id,
          'parent': {
              'type': parent_type,
              'id': parent_id
          }
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

  UpdateIAMPolicy(context, resources, project_id)

  UpdateSharedVPCSettings(context, resources, project_id)

  return {'resources': resources}

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
