from helper import config_merger
import json


def GenerateConfig(context):
    """Main entry point for Deployment Manager logic"""

    module = "project"
    cc = config_merger.ConfigContext(context.properties, module)

    return {
        'resources': [
            #   {
            #  'name': 'sample-named-h-project1',
            #   'type': 'project.py',
            #  'properties': cc.configs['project_module']
            #}
        ],
        'outputs': [{
            'name':
            'outp_3',
            'value':
            json.dumps(
                cc.configs, sort_keys=True, indent=4, separators=(',', ': '))
        }]
    }
