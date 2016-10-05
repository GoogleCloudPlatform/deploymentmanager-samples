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

  cluster_type = ''.join([context.env['project'], '/',
                          context.properties['clusterType']])

  collection_prefix = '/api/v1/namespaces/{namespace}/'
  rc_collection = collection_prefix + 'replicationcontrollers'
  service_collection = collection_prefix + 'services'

  name_prefix = context.env['deployment'] + '-' + context.env['name']
  port = context.properties['port']

  resources = [{
      'name': name_prefix,
      'type': cluster_type + ':' + service_collection,
      'properties': {
          'apiVersion': 'v1',
          'kind': 'Service',
          'namespace': 'default',
          'metadata': {
              'name': name_prefix
          },
          'spec': {
              # Creates an external IP through network load-balancer.
              'type': 'LoadBalancer',
              'ports': [{
                  'port': port,
                  'targetPort': port,
                  'protocol': 'TCP'
              }],
              'selector': {
                  'name': name_prefix
              }
          }
      }
  }, {
      'name': name_prefix + '-rc',
      'type': cluster_type + ':' + rc_collection,
      'properties': {
          'apiVersion': 'v1',
          'kind': 'ReplicationController',
          'namespace': 'default',
          'metadata': {
              'name': name_prefix + '-rc'
          },
          'spec': {
              'template': {
                  'metadata': {
                      'labels': {
                          'name': name_prefix
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
