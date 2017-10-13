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

"""Creates a KMS key."""

def GenerateConfig(context):
  """Generates configuration."""

  key_ring = {
    'name': 'keyRing',
    'type': 'gcp-types/cloudkms-v1:projects.locations.keyRings',
    'properties': {
      'parent': 'projects/' + context.env['project'] + '/locations/' + context.properties['region'],
      'keyRingId': context.env['deployment'] + '-key-ring'
    }
  }

  crypto_key = {
    'name': 'cryptoKey',
    'type': 'gcp-types/cloudkms-v1:projects.locations.keyRings.cryptoKeys',
    'properties': {
      'parent': '$(ref.keyRing.name)',
      'cryptoKeyId': context.env['deployment'] + '-crypto-key',
      'purpose': 'ENCRYPT_DECRYPT'
    }
  }

  resources = [key_ring, crypto_key]
  outputs = [{
    'name': 'primaryVersion',
    'value': '$(ref.cryptoKey.primary)'
  }]

  return { 'resources': resources, 'outputs': outputs }
