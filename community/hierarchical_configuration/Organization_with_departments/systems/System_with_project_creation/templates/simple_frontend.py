from helper import config_merger
COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'


def GlobalComputeUrl(project, collection, name):
    return ''.join([
        COMPUTE_URL_BASE, 'projects/', project, '/global/', collection, '/',
        name
    ])


def ZonalComputeUrl(project, zone, collection, name):
    return ''.join([
        COMPUTE_URL_BASE, 'projects/', project, '/zones/', zone, '/',
        collection, '/', name
    ])


def GenerateConfig(context):
    """Generate configuration."""

    module = "frontend"
    cc = config_merger.ConfigContext(context.properties, module)

    name_prefix = cc.configs["Org_Name"] + cc.configs["ProjectAbbreviation"] + context.properties["envName"] + module
    i_name_prefix = cc.configs["Org_Name"] + "-" + cc.configs["ProjectAbbreviation"] + "-" + context.properties["envName"] + module

    instance = {
        'zone':
        cc.configs['zone'],
        'machineType':
        ZonalComputeUrl(context.env['project'], cc.configs['zone'],
                        'machineTypes',
                        cc.configs['Instance']['InstanceType']),
        'disks': [{
            'deviceName': 'boot',
            'type': 'PERSISTENT',
            'autoDelete': True,
            'boot': True,
            'initializeParams': {
                'diskName':
                name_prefix.replace(' ', '-').lower() + '-disk',
                'sourceImage':
                GlobalComputeUrl(cc.configs['Instance']['OSFamily'],
                                 'images/family',
                                 cc.configs['Instance']['OSVersion'])
            },
        }],
        'networkInterfaces': [{
            'accessConfigs': [{
                'name': 'external-nat',
                'type': 'ONE_TO_ONE_NAT'
            }],
            'network':
            GlobalComputeUrl(context.env['project'], 'networks', 'default')
        }]
    }

    # Resources to return.
    resources = {
        'resources': [{
            'name': i_name_prefix.replace(' ', '-').lower() + '-i',
            'type': 'compute.v1.instance',
            'properties': instance
        }]
    }

    return resources
