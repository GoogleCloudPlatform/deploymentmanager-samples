from helper import config_merger
from helper import naming_helper
import json


def GenerateConfig(context):
    """Main entry point for Deployment Manager logic"""

    module = "project"

    cc = config_merger.ConfigContext(context.properties, module)

    naming = naming_helper.NamingHelper(cc)

    return {
        'resources': [
            #{
            #    'name': naming.getProjectName('example-tool'),
            #    'type': 'project.py',
            #    'properties': cc.configs['project_module']
            #}
        ],
        'outputs': [{
            'name':
            'outp_3',
            'value':
            json.dumps(
                naming.configs,
                sort_keys=True,
                indent=4,
                separators=(',', ': '))
        }]
    }
