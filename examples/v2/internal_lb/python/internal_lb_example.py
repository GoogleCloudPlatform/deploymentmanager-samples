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
"""Creates a full internal load balancer sample."""


def TestingResources(network_ref, subnet_ref, region, zones):
  """Get the resources necessary to test an internal load balancer.

  This creates a test service, and a standalone client.

  Args:
    network_ref: A reference to a GCE network for resources to act in.
    subnet_ref: A reference to a GCE subnetwork for resources to act in.
    region: The region to deploy the load balancer.
    zones: A list of zones to deploy the service.

  Returns:
    A list of resource definitions.
  """
  return [{
      'name': 'test-service',
      'type': 'test_service.py',
      'properties': {
          'network': network_ref,
          'subnet': subnet_ref,
          'region': region,
          'zones': zones
      }
  }, {
      'name': 'standalone-client',
      'type': 'standalone_test_instance.py',
      'properties': {
          'network': network_ref,
          'subnet': subnet_ref,
          'zone': zones[0]
      }
  }]


def GenerateConfig(context):
  """Generate Deployment Manager configuration.

  Args:
    context: The context object provided by Deployment Manager.

  Returns:
    A config object for Deployment Manager (basically a dict with resources).
  """

  region = context.properties['region']
  prefix = region + '-' + context.env['deployment']

  network_name = prefix + '-network'
  subnet_name = prefix + '-subnetwork'

  network_ref = '$(ref.{}.selfLink)'.format(network_name)
  subnet_ref = '$(ref.{}.selfLink)'.format(subnet_name)

  # Basic network, firewall rules, and load balancer
  resources = [{
      'name': network_name,
      'type': 'compute.v1.network',
      'properties': {
          'autoCreateSubnetworks': False,
      }
  }, {
      'name': subnet_name,
      'type': 'compute.v1.subnetwork',
      'properties': {
          'region': region,
          'privateIpGoogleAccess': False,
          'ipCidrRange': '10.128.0.0/20',
          'network': network_ref,
      }
  }, {
      'name': prefix + '-allow-internal-traffic-firewall-rule',
      'type': 'compute.v1.firewall',
      'properties': {
          'network':
              network_ref,
          'sourceRanges': ['10.128.0.0/20'],
          'allowed': [{
              'IPProtocol': 'tcp',
              'ports': ['22']
          }, {
              'IPProtocol': 'tcp',
              'ports': ['3389']
          }, {
              'IPProtocol': 'icmp',
          }],
          'direction':
              'INGRESS',
          'priority':
              1000,
      }
  }, {
      'name': 'internal-lb',
      'type': 'internal_lb.py',
      'properties': {
          'network': network_ref,
          'subnet': subnet_ref,
          'instance-groups': '$(ref.test-service.instance-groups)',
          'instance-tag': '$(ref.test-service.instance-tag)',
          'region': region,
      }
  }]

  resources += TestingResources(network_ref, subnet_ref, region,
                                context.properties['zones'])

  return {
      'resources': resources,
      'outputs': [{
          'name': 'ip',
          'value': '$(ref.internal-lb.ip)'
      }]
  }
