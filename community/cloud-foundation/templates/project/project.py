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
"""Creates a single project with specified service accounts and APIs enabled."""
import copy


def generate_config(context):
    """ Entry point for the deployment resources """

    project_id = context.env['name']
    project_name = context.properties.get('name', project_id)

    # ensure parent ID is a string
    context.properties['parent']['id'] = str(context.properties['parent']['id'])

    resources = [
        {
            'name': 'project',
            'type': 'cloudresourcemanager.v1.project',
            'properties':
                {
                    'name': project_name,
                    'projectId': project_id,
                    'parent': context.properties['parent']
                }
        },
        {
            'name': 'billing',
            'type': 'deploymentmanager.v2.virtual.projectBillingInfo',
            'properties':
                {
                    'name':
                        'projects/$(ref.project.projectId)',
                    'billingAccountName':
                        'billingAccounts/' +
                        context.properties['billingAccountId']
                }
        }
    ]

    api_resources, api_names_list = activate_apis(context.properties)
    resources.extend(api_resources)
    resources.extend(create_service_accounts(context.properties))
    resources.extend(patch_iam_policies(context.properties))
    resources.extend(create_bucket(context.properties))
    resources.extend(create_shared_vpc(project_id, context.properties))

    if context.properties.get('removeDefaultVPC', True):
        resources.extend(delete_default_network(api_names_list))

    if context.properties.get('removeDefaultSA', True):
        resources.extend(delete_default_service_account(api_names_list))

    return {
        'resources':
            resources,
        'outputs':
            [
                {
                    'name': 'projectId',
                    'value': '$(ref.project.projectId)'
                },
                {
                    'name': 'usageExportBucketName',
                    'value': '$(ref.project.projectId)-usage-export'
                },
                {
                    'name':
                        'serviceAccountDisplayName',
                    'value':
                        '$(ref.project.projectNumber)@cloudservices.gserviceaccount.com'  # pylint: disable=line-too-long
                }
            ]
    }


def activate_apis(properties):
    """Resources for API activation"""

    concurrent_api_activation = properties.get('concurrentApiActivation')
    apis = properties.get('activateApis', [])

    # Enable storage-component API if usage export bucket enabled
    if (
        properties.get('usageExportBucket') and
        'storage-component.googleapis.com' not in apis
    ):
        apis.append('storage-component.googleapis.com')

    resources = []
    api_names_list = ['billing']
    for api in properties.get('activateApis', []):
        depends_on = ['billing']
        # Serialize the activation of all the apis by making apis[n]
        # depend on apis[n-1]
        if resources and not concurrent_api_activation:
            depends_on.append(resources[-1]['name'])

        api_name = 'api-' + api
        api_names_list.append(api_name)
        resources.append(
            {
                'name': api_name,
                'type': 'deploymentmanager.v2.virtual.enableService',
                'metadata': {
                    'dependsOn': depends_on
                },
                'properties':
                    {
                        'consumerId': 'project:' + '$(ref.project.projectId)',
                        'serviceName': api
                    }
            }
        )

    # Return the API resources so other resources can use them as dependencies
    # to ensure that they are created first. For example the default VPC or
    # default service account
    return resources, api_names_list


def create_service_accounts(properties):
    """Resources for service accounts"""

    resources = []
    for service_account in properties['serviceAccounts']:
        resources.append(
            {
                'name': 'service-account-' + service_account,
                'type': 'iam.v1.serviceAccount',
                'properties':
                    {
                        'accountId': service_account,
                        'displayName': service_account,
                        'projectId': '$(ref.project.projectId)'
                    }
            }
        )
    return resources


def create_bucket(properties):
    """Resources for usage export bucket"""

    resources = []
    if properties.get('usageExportBucket'):
        bucket_name = '$(ref.project.projectId)-usage-export'

        # Create bucket
        resources.append(
            {
                'name': 'create-usage-export-bucket',
                'type': 'gcp-types/storage-v1:buckets',
                'properties':
                    {
                        'project': '$(ref.project.projectId)',
                        'name': bucket_name
                    },
                'metadata':
                    {
                        'dependsOn': ['api-storage-component.googleapis.com']
                    }
            }
        )

        # Set the project's usage export bucket
        resources.append(
            {
                'name':
                    'set-usage-export-bucket',
                'action':
                    'gcp-types/compute-v1:compute.projects.setUsageExportBucket',  # pylint: disable=line-too-long
                'properties':
                    {
                        'project': '$(ref.project.projectId)',
                        'bucketName': 'gs://' + bucket_name
                    },
                'metadata': {
                    'dependsOn': ['create-usage-export-bucket']
                }
            }
        )
    return resources


def patch_iam_policies(properties):
    """Resources for patch IAM policies"""

    iam_policy_patch = properties.get('iamPolicyPatch', {})
    set_dm_service_account_as_owner = properties.get(
        'setDMServiceAccountAsOwner'
    )

    resources = []
    if iam_policy_patch or set_dm_service_account_as_owner:
        policies_to_add = iam_policy_patch.get('add', [])
        policies_to_remove = iam_policy_patch.get('remove', [])

        # Set DM service account as owner if enabled
        if set_dm_service_account_as_owner:
            svc_acct = 'serviceAccount:$(ref.project.projectNumber)@cloudservices.gserviceaccount.com'  # pylint: disable=line-too-long

            # Add the default DM service account as a member of the
            # first policy in the "add" list with an "owner role" (if
            # DM service account isn't already a member)
            for idx, policy in enumerate(policies_to_add):
                if (
                    policy['role'] == 'roles/owner' and
                    svc_acct not in policies_to_add[idx]['members']
                ):
                    policies_to_add[idx]['members'].append(svc_acct)
                    break
            # If no "owner role" is found in the "add policy", add it
            # to the list
            else:
                policies_to_add.append(
                    {
                        'role': 'roles/owner',
                        'members': [svc_acct]
                    }
                )

        resources.extend(
            [
                {
                    # Get the IAM policy first so that we do not remove
                    # any existing bindings.
                    'name': 'get-iam-policy',
                    'action': 'gcp-types/cloudresourcemanager-v1:cloudresourcemanager.projects.getIamPolicy', # pylint: disable=line-too-long
                    'properties': {
                        'resource': '$(ref.project.projectId)'
                    },
                    'metadata':
                        {
                            'dependsOn': [
                                'api-{}'.format(api) for api in
                                properties.get('activateApis', [])
                            ],
                            'runtimePolicy': ['UPDATE_ALWAYS']
                        }
                },
                {
                    # Set the IAM policy patching the existing policy
                    # with what ever is currently in the config.
                    'name': 'patch-iam-policy',
                    'action': 'gcp-types/cloudresourcemanager-v1:cloudresourcemanager.projects.setIamPolicy', # pylint: disable=line-too-long
                    'properties':
                        {
                            'resource': '$(ref.project.projectId)',
                            'policy': '$(ref.get-iam-policy)',
                            'gcpIamPolicyPatch':
                                {
                                    'add': policies_to_add,
                                    'remove': policies_to_remove
                                }
                        }
                }
            ]
        )
    return resources


def create_shared_vpc(project_id, properties):
    """ Configure project Shared VPC properties """

    resources = []

    service_project = properties.get('sharedVPC')
    if service_project:
        resources.append(
            {
                'name': project_id + '-attach-xpn-service-' + service_project,
                'type': 'compute.beta.xpnResource',
                'metadata': {
                    'dependsOn': ['api-compute.googleapis.com']
                },
                'properties':
                    {
                        'project': service_project,
                        'xpnResource':
                            {
                                'id': '$(ref.project.projectId)',
                                'type': 'PROJECT',
                            }
                    }
            }
        )
    elif properties.get('sharedVPCHost'):
        resources.append(
            {
                'name': project_id + '-xpn-host',
                'type': 'compute.beta.xpnHost',
                'metadata': {
                    'dependsOn': ['api-compute.googleapis.com']
                },
                'properties': {
                    'project': '$(ref.project.projectId)'
                }
            }
        )

    return resources


def delete_default_network(api_names_list):
    """ Delete the default network """

    icmp_name = 'delete-default-allow-icmp'
    internal_name = 'delete-default-allow-internal'
    rdp_name = 'delete-default-allow-rdp'
    ssh_name = 'delete-default-allow-ssh'

    resource = [
        {
            'name': icmp_name,
            'action': 'gcp-types/compute-beta:compute.firewalls.delete',
            'metadata': {
                'dependsOn': api_names_list
            },
            'properties':
                {
                    'firewall': 'default-allow-icmp',
                    'project': '$(ref.project.projectId)',
                }
        },
        {
            'name': internal_name,
            'action': 'gcp-types/compute-beta:compute.firewalls.delete',
            'metadata': {
                'dependsOn': api_names_list
            },
            'properties':
                {
                    'firewall': 'default-allow-internal',
                    'project': '$(ref.project.projectId)',
                }
        },
        {
            'name': rdp_name,
            'action': 'gcp-types/compute-beta:compute.firewalls.delete',
            'metadata': {
                'dependsOn': api_names_list
            },
            'properties':
                {
                    'firewall': 'default-allow-rdp',
                    'project': '$(ref.project.projectId)',
                }
        },
        {
            'name': ssh_name,
            'action': 'gcp-types/compute-beta:compute.firewalls.delete',
            'metadata': {
                'dependsOn': api_names_list
            },
            'properties':
                {
                    'firewall': 'default-allow-ssh',
                    'project': '$(ref.project.projectId)',
                }
        }
    ]

    # Ensure the firewall rules are removed before deleting the VPC
    network_dependency = copy.copy(api_names_list)
    network_dependency.extend([icmp_name, internal_name, rdp_name, ssh_name])

    resource.append(
        {
            'name': 'delete-default-network',
            'action': 'gcp-types/compute-beta:compute.networks.delete',
            'metadata': {
                'dependsOn': network_dependency
            },
            'properties':
                {
                    'network': 'default',
                    'project': '$(ref.project.projectId)'
                }
        }
    )

    return resource


def delete_default_service_account(api_names_list):
    """ Delete the default service account """

    resource = [
        {
            'name': 'delete-default-sa',
            'action': 'gcp-types/iam-v1:iam.projects.serviceAccounts.delete',
            'metadata':
                {
                    'dependsOn': api_names_list,
                    'runtimePolicy': ['CREATE']
                },
            'properties':
                {
                    'name':
                        'projects/$(ref.project.projectId)/serviceAccounts/$(ref.project.projectNumber)-compute@developer.gserviceaccount.com'  # pylint: disable=line-too-long
                }
        }
    ]

    return resource
