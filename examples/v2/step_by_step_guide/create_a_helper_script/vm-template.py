"""Creates the virtual machine."""

# `common.py` is imported below.
import common

COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'


def GenerateConfig(context):
  """Generates configuration of a VM."""
  resources = [{
      'name': common.GenerateMachineName('myfrontend', 'prod'),
      'type': 'compute.v1.instance',
      'properties': {
          'zone': 'us-central1-f',
          'machineType': COMPUTE_URL_BASE + 'projects/' + context.env['project']
                         + '/zones/us-central1-f/machineTypes/f1-micro',
          'disks': [{
              'deviceName': 'boot',
              'type': 'PERSISTENT',
              'boot': True,
              'autoDelete': True,
              'initializeParams': {
                  'sourceImage': COMPUTE_URL_BASE + 'projects/'
                                 'debian-cloud/global/images/family/debian-9'}
          }],
          'networkInterfaces': [{
              'network': COMPUTE_URL_BASE + 'projects/' + context.env['project']
                         + '/global/networks/default',
              'accessConfigs': [{
                  'name': 'External NAT',
                  'type': 'ONE_TO_ONE_NAT'
              }]
          }]
      }
  }]
  return {'resources': resources}
 
