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

"""Subnetworks Template."""
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
      'autoCreateSubnetworks': False
  })
  subnetwork = ComputeResource('subnet', compute_constants.SUBNETWORKS, {
      'network': network.SelfLink(),
      'region': region,
      'ipCidrRange': properties['ipCidrRange'],
  })
  if 'secondaryIpRanges' in properties:
    subnetwork['secondaryIpRanges'] = properties['secondaryIpRanges']
  if 'enableFlowLogs' in properties:
    subnetwork['enableFlowLogs'] = properties['enableFlowLogs']
  if 'allowSubnetCidrRoutesOverlap' in properties:
    subnetwork['allowSubnetCidrRoutesOverlap'] = properties['allowSubnetCidrRoutesOverlap']
  if 'privateIpGoogleAccess' in properties:
    subnetwork['privateIpGoogleAccess'] = properties['privateIpGoogleAccess']
  if 'description' in properties:
    subnetwork['description'] = properties['description']
  return Resources()
