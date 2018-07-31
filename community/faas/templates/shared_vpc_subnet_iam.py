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
""" Grant IAM roles for a user on a shared VPC subnet """


def generate_config(context):
    """ Entry point for the deployment resources """

    project_id = context.env['project']

    resources = []
    for i, subnet in enumerate(context.properties['subnets'], 1):
        policy_name = 'iam-subnet-policy-{}'.format(i)

        policies_to_add = [
            {
                'role': 'roles/compute.networkUser',
                'members': subnet['members']
            }
        ]

        resources.append(
            {
                'name': policy_name,
                'type': 'gcp-types/compute-beta:compute.subnetworks.setIamPolicy',  # pylint: disable=line-too-long
                'properties':
                    {
                        'name': subnet['subnetId'],
                        'project': context.env['project'],
                        'region': subnet['region'],
                        'bindings': policies_to_add
                    }
            }
        )

    return {"resources": resources}
