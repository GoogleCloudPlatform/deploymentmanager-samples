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

"""Cloud Router Template."""
import compute_constants
import compute_resource_util
from compute_resource_util import ComputeResource
from compute_resource_util import Resources


def GenerateConfig(context):
  """Generate template config based on python objects."""
  properties = context.properties
  region = properties['region']
  compute_resource_util.SetContext(context)

  network = ComputeResource('network', compute_constants.NETWORKS, {
    'autoCreateSubnetworks': True
  })
  vpn_gateway = ComputeResource('vpg', compute_constants.TARGETVPNGATEWAYS, {
      'network': network.SelfLink(),
      'region': region
  })
  ip = ComputeResource('static-ip', compute_constants.ADDRESSES,
                       {'region': region})
  esp_rule = ComputeResource(
      'esp-rule', compute_constants.FORWARDINGRULES, {
          'IPProtocol': 'ESP',
          'IPAddress': ip.Ref('address'),
          'region': region,
          'target': vpn_gateway.SelfLink()
      })
  udp4500_rule = ComputeResource(
      'udp-4500-rule', compute_constants.FORWARDINGRULES, {
          'IPProtocol': 'UDP',
          'IPAddress': ip.Ref('address'),
          'region': region,
          'target': vpn_gateway.SelfLink(),
          'portRange': 4500
      })
  udp500_rule = ComputeResource(
      'udp-500-rule', compute_constants.FORWARDINGRULES, {
          'IPProtocol': 'UDP',
          'IPAddress': ip.Ref('address'),
          'region': region,
          'target': vpn_gateway.SelfLink(),
          'portRange': 500
      })
  cloud_router = ComputeResource('cloud-router', compute_constants.ROUTERS, {
      'region': region,
      'network': network.SelfLink(),
      'asn': properties['asn']
  })
  ComputeResource(
      'vpn-tunnel', compute_constants.VPNTUNNELS, {
          'region':
              region,
          'ikeVersion':
              2,
          'sharedSecret':
              properties['sharedSecret'],
          'peerIp':
              properties['peerAddress'],
          'router':
              cloud_router.SelfLink(),
          'targetVpnGateway':
              vpn_gateway.SelfLink(),
          'description':
              'Must be deployed after ' + esp_rule.SelfLink() + ' ' +
              udp500_rule.SelfLink() + ' ' + udp4500_rule.SelfLink()
      })

  return Resources()
