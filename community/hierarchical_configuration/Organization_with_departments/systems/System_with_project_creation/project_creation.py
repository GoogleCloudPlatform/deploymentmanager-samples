from helper import config_merger
import json

def GenerateConfig(context):
  """Main entry point for Deployment Manager logic"""
  
  module = "project"
  cc = config_merger.ConfigContext(context.properties, module)
  
  return {
      'resources': [
      {
      'name': 'sample-named-sample-project1',
      'type': 'project.py',
      'properties': cc.configs['project_module']
  }
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
          'name': 'outp_3',
          'value': json.dumps(cc.configs, sort_keys=True, indent=4, separators=(',', ': '))
      }]
     
  }