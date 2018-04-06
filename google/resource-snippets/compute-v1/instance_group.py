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

"""Instance group template."""
import compute_constants
import compute_resource_util
from compute_resource_util import ComputeResource
from compute_resource_util import Resources


def GenerateConfig(context):
  """Generate template config based on python objects."""
  compute_resource_util.SetContext(context)
  properties = context.properties
  assert ('region' in properties) ^ ('zone' in properties), (
      'Need to specify exactly only one from zone or region')
  if 'region' in properties:
    ComputeResource('ig', compute_constants.REGIONINSTANCEGROUPS, {
        'region': properties['region']
    })
  else:
    ComputeResource('ig', compute_constants.INSTANCEGROUPS, {
        'zone': properties['zone']
    })
  return Resources()
