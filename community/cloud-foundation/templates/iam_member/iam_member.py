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

    resources = []
    i = 0
    for role in context.properties['roles']:
        for i, member in enumerate(role['members']):
            policy_get_name = 'get-iam-policy-{}-{}'.format(project_id, i)
            resources.append(
                {
                    'name': policy_get_name,
                    'type': 'gcp-types/cloudresourcemanager-v1:virtual.projects.iamMemberBinding',
                    'properties':
                    {
                        'resource': project_id,
                        'role': role['role'],
                        'member': member
                    }
                }
            )
            i += 1

    return {"resources": resources}
