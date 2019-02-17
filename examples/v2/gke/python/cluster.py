# Copyright 2016 Google Inc. All rights reserved.
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
"""Create configuration to deploy GKE cluster."""


def GenerateConfig(context):
  """Generate YAML resource configuration."""

  clusterName = context.properties['clusterName']

  resources = [
      {
          'name': clusterName,
          'type': 'container.v1.cluster',
          'properties': {
              'zone': context.properties['zone'],
              'cluster': {
                  'name': clusterName,
                  'initialNodeCount': context.properties['initialNodeCount'],
                  'nodeConfig': {
                      'oauthScopes': [
                          'https://www.googleapis.com/auth/' + s
                          for s in [
                              'compute',
                              'devstorage.read_only',
                              'logging.write',
                              'monitoring'
                          ]
                      ]
                  }
              }
          }
      }
  ]
  outputs = []
  resources.append({
        'name': clusterName + '-provider',
        'type': 'deploymentmanager.v2beta.typeProvider',
        'properties': {
            'options': {
                'validationOptions': {
                    # Kubernetes API accepts ints, in fields they annotate
                    # with string. This validation will show as warning
                    # rather than failure for Deployment Manager.
                    # https://github.com/kubernetes/kubernetes/issues/2971
                    'schemaValidation': 'IGNORE_WITH_WARNINGS'
                },
                # According to kubernetes spec, the path parameter 'name' and 'namespace'
                # *must* be set inside the metadata field.
                # https://github.com/kubernetes/community/blob/master/contributors/devel/sig-architecture/api-conventions.md#metadata
                # The input mappings will map the values to path parameters
                'inputMappings': [{
                    'fieldName': 'name',
                    'location': 'PATH',
                    'methodMatch': '^(get|delete|put|patch|post)$',
                    'value': '$.resource.properties.metadata.name'
                }, {
                    'fieldName': 'namespace',
                    'location': 'PATH',
                    'methodMatch': '^(get|delete|put|patch|post)$',
                    'value': '$.resource.properties.metadata.namespace'
                }, {
                    'fieldName': 'Authorization',
                    'location': 'HEADER',
                    'value': '$.concat("Bearer ",'
                             '$.googleOauth2AccessToken())'
                }]
            },
            'descriptorUrl': 'https://$(ref.' + clusterName + '.endpoint)/openapi/v2'
        }
    })
  outputs.append({
        'name': 'clusterType',
        'value': clusterName + '-provider'
  })

  return {'resources': resources, 'outputs': outputs}
