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
"""Creates several instances and instance groups as a fake service."""

TARGET_TAG = 'load-balanced'


def ComputeInstance(igm_name, instance_name, zone, machine_type, properties):
  return {
      'name': instance_name,
      'type': 'compute.v1.instance',
      'metadata': {
          'dependsOn': [igm_name],
      },
      'properties': {
          'zone':
              zone,
          'machineType':
              machine_type,
          'tags': {
              'items': [TARGET_TAG],
          },
          'networkInterfaces': [{
              'network':
                  properties['network'],
              'subnetwork':
                  properties['subnet'],
              'accessConfigs': [{
                  'name': 'External NAT',
                  'type': 'ONE_TO_ONE_NAT'
              }]
          }],
          'disks': [{
              'type': 'PERSISTENT',
              'boot': True,
              'mode': 'READ_WRITE',
              'autoDelete': True,
              'deviceName': 'boot',
              'initializeParams': {
                  'sourceImage': (
                      'https://www.googleapis.com/compute/v1/'
                      'projects/debian-cloud/global/images/family/debian-9'),
              }
          }],
          'metadata': {
              'items': [{
                  'key':
                      'startup-script',
                  'value': ('echo "RUNNING STARTUP SCRIPT"\n'
                            'gcloud compute instance-groups unmanaged '
                            'add-instances {instance_group} '
                            '--instances {instance} --zone {zone}\n'
                            'sudo apt-get update\n'
                            'sudo apt-get install apache2 -y\n'
                            'sudo a2ensite default-ssl\n'
                            'sudo a2enmod ssl\n'
                            'sudo service apache2 restart\n'
                            "echo '<!doctype html><html><body><h1>{instance}"
                            "</h1></body></html>'"
                            ' | sudo tee /var/www/html/index.html\n').format(
                                instance_group=igm_name,
                                instance=instance_name,
                                zone=zone)
              }]
          },
          'serviceAccounts': [{
              'email': 'default',
              'scopes': [
                  'https://www.googleapis.com/auth/compute',
              ]
          }]
      }
  }


def GenerateConfig(context):
  """Build the config.

  Args:
    context: The context object provided by Deployment Manager.

  Returns:
    A config object for Deployment Manager (basically a dict with resources).
  """
  properties = context.properties
  prefix = context.env['deployment']
  resources = []
  igms = []

  for zone in properties['zones']:
    instance_name = prefix + '-instance-' + zone
    igm_name = prefix + '-instance-group-' + zone
    machine_type = 'projects/{}/zones/{}/machineTypes/{}'.format(
        context.env['project'], zone, properties['machine-type'])

    igms.append({'group': '$(ref.' + igm_name + '.selfLink)'})
    resources.append({
        'name': igm_name,
        'type': 'compute.v1.instanceGroup',
        'properties': {
            'zone': zone,
            'network': properties['network'],
        }
    })

    resources.append(ComputeInstance(igm_name,
                                     instance_name,
                                     zone,
                                     machine_type,
                                     properties))

  return {
      'resources':
          resources,
      'outputs': [{
          'name': 'instance-groups',
          'value': igms
      }, {
          'name': 'instance-tag',
          'value': TARGET_TAG
      }]
  }
