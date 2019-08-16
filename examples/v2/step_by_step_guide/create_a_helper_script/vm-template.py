"""Creates the virtual machine."""

# `common.py` is imported below.
{% import 'common.py' as common %}

COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'


def GenerateConfig(context):
  """Creates the virtual machine with environment variables."""
  
  # The `name` listing has been changed to use the helper script.
  resources = [{
      'name': {{ common.GenerateMachineName("myfrontend", "prod") }},
      'type': 'compute.v1.instance',
      'properties': {
          'zone': context.properties['zone'],
          'machineType': ''.join([COMPUTE_URL_BASE, 'projects/',
                                  context.env['project'], '/zones/',
                                  context.properties['zone'], '/machineTypes/',
                                  context.properties['machineType']]),
          'disks': [{
              'deviceName': 'boot',
              'type': 'PERSISTENT',
              'boot': True,
              'autoDelete': True,
              'initializeParams': {
                  'sourceImage': ''.join([COMPUTE_URL_BASE, 'projects/',
                                          'debian-cloud/global/',
                                          'images/family/debian-9'])
              }
          }],
          'networkInterfaces': [{
              'network': '$(ref.' + context.properties['network']
                         + '.selfLink)',
              'accessConfigs': [{
                  'name': 'External NAT',
                  'type': 'ONE_TO_ONE_NAT'
              }]
          }]
      }
  }]
  return {'resources': resources}

