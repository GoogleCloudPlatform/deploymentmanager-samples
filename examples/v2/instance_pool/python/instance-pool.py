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
"""Python template for creating a pool of similar instances."""


def GenerateConfig(context):
  """Generate the yaml config for a pool of instances."""
  resources = []
  for index in range(1, context.properties['count'] + 1):
    resources.append(GenerateInstanceConfig(context, index))
  return {'resources': resources}


def GenerateInstanceConfig(context, index):
  """Helper method to create the config for a single compute instance."""
  name_prefix = ''.join([context.properties['namePrefix'], '-',
                         context.env['deployment'], '-', str(index)])
  machine_type = ''.join(['https://www.googleapis.com/compute/v1/projects/',
                          context.env['project'], '/zones/',
                          context.properties['zone'], '/machineTypes/',
                          context.properties['machineType']])
  boot_disk_config = GetBootDiskConfig(name_prefix + '-disk',
                                       context.properties['image'])
  network_config_url = ''.join(
      ['https://www.googleapis.com/compute/v1/projects/',
       context.env['project'], '/global/networks/default'])
  network_config = GetNetworkConfig(context.properties['hasExternalIp'],
                                    network_config_url)

  instance = {
      'type': 'compute.v1.instance',
      'name': name_prefix,
      'properties': {
          'zone': context.properties['zone'],
          'machineType': machine_type,
          'disks': [boot_disk_config],
          'networkInterfaces': [network_config]
      }
  }
  return instance


def GetBootDiskConfig(disk_name, source_image):
  """Helper method to create a boot disk property."""
  return {
      'deviceName': 'boot',
      'type': 'PERSISTENT',
      'boot': True,
      'autoDelete': True,
      'initializeParams': {
          'diskName': disk_name,
          'sourceImage': source_image,
      }
  }


def GetNetworkConfig(has_external_ip, network):
  """Helper method to create a network config."""
  network_interfaces = {
      'network': network
  }
  if has_external_ip:
    network_interfaces['accessConfigs'] = [{
        'name': 'external-nat',
        'type': 'ONE_TO_ONE_NAT'
    }]
  return network_interfaces
