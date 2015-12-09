# Copyright 2015 Google Inc. All rights reserved.
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

"""Generates configuration for a network load balancer."""


def GenerateConfig(context):
  """Generates config."""

  prefix = context.env['name']

  hc_name = prefix + '-hc'
  tp_name = prefix + '-tp'
  fr_name = prefix + '-fr'

  port = context.properties['port']
  region = context.properties['region']

  resources = [{
      'name': hc_name,
      'type': 'compute.v1.httpHealthCheck',
      'properties': {
          'port': port,
          'requestPath': '/_ah/health'
      }
  }, {
      'name': tp_name,
      'type': 'compute.v1.targetPool',
      'properties': {
          'region': region,
          'healthChecks': ['$(ref.' + hc_name + '.selfLink)']
      }
  }, {
      'name': fr_name,
      'type': 'compute.v1.forwardingRule',
      'properties': {
          'region': region,
          'portRange': port,
          'target': '$(ref.' + tp_name + '.selfLink)'
      }
  }]

  return {'resources': resources}
