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

"""Autoscaler/IGM/InstanceTemplate multiversion test."""
import compute_constants
import compute_resource_util
from compute_resource_util import ComputeResource
from compute_resource_util import Resources


def GenerateConfig(context):
  """Generate template config based on python objects."""
  compute_resource_util.SetContext(context)
  properties = context.properties
  disk_name = context.env['deployment'] + '-' + 'disk'
  image = 'projects/debian-cloud/global/images/debian-7-wheezy-v20140619'
  default_network = 'global/networks/default'
  assert ('region' in properties) ^ ('zone' in properties), (
      'Need to specify exactly only one from zone or region')
  template = ComputeResource(
      'template', compute_constants.INSTANCETEMPLATES, {
          'properties': {
              'machineType':
                  'f1-micro',
              'disks': [{
                  'deviceName': 'boot',
                  'boot': True,
                  'autoDelete': True,
                  'mode': 'READ_WRITE',
                  'initializeParams': {
                      'diskName': disk_name,
                      'sourceImage': image
                  },
                  'type': 'PERSISTENT'
              }],
              'networkInterfaces': [{
                  'network': default_network
              }]
          }
      })
  if 'region' in properties:
    igm = ComputeResource(
        'igm', compute_constants.REGIONINSTANCEGROUPMANAGERS, {
            'region': properties['region'],
            'size': properties['size'],
            'baseInstanceName': context.env['deployment'] + '-instance',
            'instanceTemplate': template.SelfLink(),
            'targetSize': 1
        })
    ComputeResource(
        'autoscaler', compute_constants.REGIONAUTOSCALERS, {
            'region':
                properties['region'],
            'autoscalingPolicy': {
                'coolDownPeriodSec': 60,
                'cpuUtilization': {
                    'utilizationTarget': 0.8
                },
                'maxNumReplicas': 3,
                'minNumReplicas': 1
            },
            'description':
                'Autoscaler created for cloud config testing purposes',
            'target':
                igm.SelfLink()
        })
  else:
    igm = ComputeResource(
        'igm', compute_constants.INSTANCEGROUPMANAGERS, {
            'zone': properties['zone'],
            'size': properties['size'],
            'baseInstanceName': context.env['deployment'] + '-instance',
            'instanceTemplate': template.SelfLink(),
            'targetSize': 1
        })
    ComputeResource(
        'autoscaler', compute_constants.AUTOSCALERS, {
            'zone':
                properties['zone'],
            'autoscalingPolicy': {
                'coolDownPeriodSec': 60,
                'cpuUtilization': {
                    'utilizationTarget': 0.8
                },
                'maxNumReplicas': 3,
                'minNumReplicas': 1
            },
            'description':
                'Autoscaler created for cloud config testing purposes',
            'target':
                igm.SelfLink()
        })
  return Resources()
