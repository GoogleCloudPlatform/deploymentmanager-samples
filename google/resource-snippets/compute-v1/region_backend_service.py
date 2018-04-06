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

"""Region backend service template."""
import compute_constants
import compute_resource_util
from compute_resource_util import ComputeResource
from compute_resource_util import Resources


def GenerateConfig(context):
  """Generate template config based on python objects."""
  properties = context.properties
  region = properties['region']
  compute_resource_util.SetContext(context)
  health_check = ComputeResource('hc', compute_constants.HEALTHCHECKS, {
      'type': 'TCP',
      'tcpHealthCheck': {
          'port': 1234
      },
      'timeoutSec': properties['timeout'],
      'description': 'Integration test tcp health check',
      'checkIntervalSec': 10,
      'unhealthyThreshold': 5,
      'healthyThreshold': 2
  })
  ComputeResource('rbs', compute_constants.REGIONBACKENDSERVICES, {
      'description': 'Regional backend service for integ test',
      'region': region,
      'loadBalancingScheme': 'INTERNAL',
      'healthChecks': [health_check.SelfLink()],
      'protocol': 'TCP',
      'timeoutSec': health_check.Ref('timeoutSec')
  })

  return Resources()
