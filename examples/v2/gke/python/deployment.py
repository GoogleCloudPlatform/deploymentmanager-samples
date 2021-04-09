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
"""Create configuration to deploy Kubernetes resources."""


def GenerateConfig(context):
  """Generate YAML resource configuration."""

  cluster_types_root = ''.join([
      context.env['project'],
      '/',
      context.properties['clusterType']
      ])
  cluster_types = {
      'Service': ''.join([
          cluster_types_root,
          ':',
          '/api/v1/namespaces/{namespace}/services/{name}'
          ]),
      'Deployment': ''.join([
          cluster_types_root,
          ':',
          '/apis/apps/v1/namespaces/{namespace}/deployments/{name}'
          ])
  }

  name_prefix = context.env['deployment'] + '-' + context.env['name']
  port = context.properties['port']

  resources = [{
      'name': name_prefix + '-service',
      'type': cluster_types['Service'],
      'properties': {
          'apiVersion': 'v1',
          'kind': 'Service',
          'namespace': 'default',
          'metadata': {
              'name': name_prefix + '-service',
              'labels': {
                  'id': 'deployment-manager'
              }
          },
          'spec': {
              'type': 'NodePort',
              'ports': [{
                  'port': port,
                  'targetPort': port,
                  'protocol': 'TCP'
              }],
              'selector': {
                  'app': name_prefix
              }
          }
      }
  }, {
      'name': name_prefix + '-deployment',
      'type': cluster_types['Deployment'],
      'properties': {
          'apiVersion': 'apps/v1',
          'kind': 'Deployment',
          'namespace': 'default',
          'metadata': {
              'name': name_prefix + '-deployment'
          },
          'spec': {
              'replicas': 1,
              'selector': {
                  'matchLabels': {
                      'app': name_prefix
                  }
              },
              'template': {
                  'metadata': {
                      'labels': {
                          'name': name_prefix + '-deployment',
                          'app': name_prefix
                      }
                  },
                  'spec': {
                      'containers': [{
                          'name': 'container',
                          'image': context.properties['image'],
                          'ports': [{
                              'containerPort': port
                          }]
                      }]
                  }
              }
          }
      }
  }]

  return {'resources': resources}
