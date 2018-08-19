from helper import config_merger
import json


def GenerateConfig(context):
    """Main entry point for Deployment Manager logic"""

    module = "frontend"
    cc = config_merger.ConfigContext(context.properties, module)

    return {
        'resources': [
            #{
            #'name': 'simple_frontend',
            #'type': 'simple_frontend.py',
            #'properties': context.properties
            #}
        ],
        'outputs': [
            #{
            #    'name': 'env_name',
            #     'value': context.properties["envName"]
            #},{
            #    'name': 'context',
            #    'value': cc.configs['CONTEXT']
            #},{
            #    'name': 'HQ_Address',
            #    'value': cc.configs['HQ_Address']
            #},{
            #    'name': 'ServiceName',
            #    'value': cc.configs['ServiceName']
            #},{
            #    'name': 'versionNR',
            #    'value': cc.configs['versionNR']
            #},
            {
                'name':
                'outp_3',
                'value':
                json.dumps(
                    cc.configs,
                    sort_keys=True,
                    indent=4,
                    separators=(',', ': '))
            }
        ]
    }
