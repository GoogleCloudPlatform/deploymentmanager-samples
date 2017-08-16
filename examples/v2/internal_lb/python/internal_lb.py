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
"""Creates a minimally configured internal load balancer."""


def GenerateConfig(context):
  """Build an internal load balancer (regionBackendService).

  Args:
    context: The context object provided by Deployment Manager.

  Returns:
    A config object for Deployment Manager (basically a dict with resources).
  """

  properties = context.properties
  prefix = context.properties['region'] + '-' + context.env['deployment']

  healthcheck_name = prefix + '-healthcheck'
  loadbalancer_name = prefix + '-loadbalancer'
  forwardingrule_name = prefix + '-forwardingrule'

  resources = [{
      'name': healthcheck_name,
      'type': 'compute.v1.healthCheck',
      'properties': {
          'type': 'TCP',
          'tcpHealthCheck': {
              'port': 80
          },
      }
  }, {
      'name': loadbalancer_name,
      'type': 'compute.v1.regionBackendService',
      'properties': {
          'region': properties['region'],
          'network': properties['network'],
          'healthChecks': ['$(ref.' + healthcheck_name + '.selfLink)'],
          'backends': properties['instance-groups'],
          'protocol': 'TCP',
          'loadBalancingScheme': 'INTERNAL',
      }
  }, {
      'name': forwardingrule_name,
      'type': 'compute.v1.forwardingRule',
      'properties': {
          'ports': [80],
          'network': properties['network'],
          'subnetwork': properties['subnet'],
          'region': properties['region'],
          'backendService': '$(ref.' + loadbalancer_name + '.selfLink)',
          'loadBalancingScheme': 'INTERNAL',
      }
  }, {
      'name': prefix + '-allow-internal-lb-firewall-rule',
      'type': 'compute.v1.firewall',
      'properties': {
          'network':
              properties['network'],
          'sourceRanges': [
              '10.128.0.0/20',
          ],
          'targetTags': [properties['instance-tag']],
          'allowed': [{
              'IPProtocol': 'tcp',
              'ports': ['80']
          }, {
              'IPProtocol': 'tcp',
              'ports': ['443']
          }]
      }
  }, {
      'name': prefix + '-allow-health-check-firewall-rule',
      'type': 'compute.v1.firewall',
      'properties': {
          'network': properties['network'],
          'sourceRanges': [
              '130.211.0.0/22',
              '35.191.0.0/16',
          ],
          'targetTags': [properties['instance-tag']],
          'allowed': [{
              'IPProtocol': 'tcp'
          }]
      }
  }]

  return {
      'resources':
          resources,
      'outputs': [{
          'name': 'ip',
          'value': '$(ref.' + forwardingrule_name + '.IPAddress)'
      }]
  }
