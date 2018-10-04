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
""" This template creates an IAM policy member. """


def generate_config(context):
    """ Entry point for the deployment resources. """

    project_id = context.env['project']
    policy_get_name = 'get-iam-policy-{}'.format(project_id)
    policy_add_name = 'add-iam-policy-{}'.format(project_id)
    policy_remove_name = 'remove-iam-policy-{}'.format(project_id)

    policies_to_add = []
    for role in context.properties['roles']:
        policies_to_add.append(
            {
                'role': role['role'],
                'members': role['members']
            }
        )

    resources = [
        {
            # Get the IAM policy first to avoid removing existing bindings.
            'name': policy_get_name,
            'action': 'gcp-types/cloudresourcemanager-v1:cloudresourcemanager.projects.getIamPolicy',  # pylint: disable=line-too-long
            'properties': {
                'resource': project_id,
            }
        },
        {
            # Set the IAM policy by patching the existing policy with the
            # config contents.
            'name': policy_add_name,
            'action': 'gcp-types/cloudresourcemanager-v1:cloudresourcemanager.projects.setIamPolicy',  # pylint: disable=line-too-long
            'properties':
                {
                    'resource': project_id,
                    'policy': '$(ref.' + policy_get_name + ')',
                    'gcpIamPolicyPatch': {
                        'add': policies_to_add,
                    }
                }
        },
        {
            'name': policy_remove_name,
            'action': 'gcp-types/cloudresourcemanager-v1:cloudresourcemanager.projects.setIamPolicy',  # pylint: disable=line-too-long
            'metadata':
                {
                    # The policy is removed when the resource is deleted.
                    'runtimePolicy': ['DELETE'],
                },
            'properties':
                {
                    'resource': project_id,
                    'policy': '$(ref.' + policy_add_name + ')',
                    'gcpIamPolicyPatch':
                        {
                            # Remove the previously created roles.
                            'remove': policies_to_add
                        }
                }
        }
    ]

    return {"resources": resources}
