# Hierarchical structure for Deployment Manager configuration

## Summary

This example helps to structure a large infrastructure defined via Deployment Manager to increase maintainability and follow general programming best practices.
Compare to a simple setup the configuration properties are split to several files to remove redundancy and provide context specific information.
This practice makes it possible to use the same codebase for multiple environments ( dev/test/prod) where the differences are defined in the configuration files. 

## PROBLEM STATEMENT
Following standard best practices a larger system should use a significant amount of external properties ( configuration parameters) to avoid hardcoding strings and logic to the generic templates.  Many of these properties are partially duplicated because of the similar environments ( like dev/test/prod ) as well as similar services ( for example all the standard services are running on a similar LAMP stack.)
This results a large set of configuration properties which can be easily messy and hard to maintain. It also potentially increases the chance of human error.

For more context, see 
[Deployment Manager Properties](https://cloud.google.com/deployment-manager/docs/configuration/templates/define-template-properties) 

## BENEFITS

* The ability to split up the configurations to multiple files increases the structure and readability of the properties.
 * Removes property duplication
* The hierarchical merge cascades the values depending on the actual context which makes the top level configuration files reusable across projects or components.
* This makes every property defined only once (except overwrites) while avoids namespacing in property names. 
 * The templates do not need to know about the actual environment ( dev/test/prod), because the appropriate configuration is loaded based on the appropriate variables. 

## OVERVIEW
The goal is to create a framework for configuration variable management for mid/large-size deployments while following [DRY](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself) principles.

* Splitting up the configuration properties to multiple files makes the system easier to review and maintain.
* The hierarchical variables makes it easy to define default values for a wider scope and overwrite them only if it's necessary. This can significantly remove duplications.
* The top part of the hierarchy ( Corporate, department, project levels) can be reused between deployments without redefining them. Those files can be centrally managed, which helps to enforce global naming conventions.
* The configuration context can be initialized in any Deployment Manager module (written in python). This can significantly decrease the required number of parameters of nested modules. ( Which may or may not a best practice.)
* The concept of "environment" supports to build up multiple copy of the same infrastructure 

![Architecture Diagram](architecture_diagram.png "Architecture diagram")

## WORKING EXAMPLE

```bash

# These 5 commands will get you up and running! This will deploy Dev,Test, Prod env as specified in the CLI argument
$ git clone https://github.com/GoogleCloudPlatform/deploymentmanager-samples.git
$ cd deploymentmanager-samples/community/hierarchical_configuration/Basic
# set project_id <your-personal-project-id> # (or add it to next gcloud commands)
# Allow bulk (glob style) imports
$ gcloud config set deployment_manager/glob_imports True
# Deploy Dev example
$ gcloud deployment-manager deployments create hierarchy-example-dev --template env_demo_project.py --properties=envName:dev
# Deploy Test example
$ gcloud deployment-manager deployments create hierarchy-example-test --template env_demo_project.py --properties=envName:test
# Deploy Prod example
$ gcloud deployment-manager deployments create hierarchy-example-prod --template env_demo_project.py --properties=envName:prod

#### comment: gcloud deployment-manager deployments describe dm-conf-dev
#### Note: Currently the describe command doesn't print the output values of the template. It can be access from the UI under "Layout" section of the deployment.

OUTPUTS                                          VALUE
Environment name defined in main.yaml            prod
CONTEXT value demonstrates overrides             We are in PROD-Frontend context
Headquarter address[City]                        Edinburgh
Headquarter address[Country]                     UK
Environment level overwrite of version number    v12.333
Module level overwrite of Service Name           FrontendApache
Full dump of aggregated context aware properties 
{  
   'ProjectOwner':'Me, myself and I',
   'ProjectAbbreviation':'SNP',
   'BackupBucket':'gs://backupbucket1',
   'ProjectId':'qwerty123456',
   'Department_name':'Department of silly walks',
   'ServiceVersion':'v3.45',
   'InstanceMax':'10',
   'envName':'prod',
   'HQ_Address':{  
      'City':'Edinburgh',
      'Country':'UK'
   },
   'versionNR':'v12.333',
   'Log_bucket':'gc://bucketname_great2',
   'CONTEXT':'We are in PROD-Frontend context',
   'Org_Name':'Sample Inc',
   'ProjectName':'Silly Naming project',
   'ServiceName':'FrontendApache',
   'InstanceMin':'3',
   'IntanceType':'micro'
}
```

Note: 
* HC_Address.Country gets overwritten on Project level while HC_Address.City holds the value coming from the Org level
* CONTEXT variable gets overwritten on every level.

## DETAILED DESIGN
If all the necessary files are imported in the .schema file properly then the ConfigContext helper class loads all of the necessary content into it's internal 'config' dictionary.

```python

class ConfigContext:

    configs = {}


    def __init__(self, context, module):
        self.configs.update(context)
        update(self.configs,self.getOrgSpecificConfig())
        update(self.configs,self.getProjectpecificConfig())
        update(self.configs,self.getEnvSpecificConfig())
        update(self.configs,self.getModuleSpecificConfig(module))
        update(self.configs,self.getEnvSpecificModuleConfig(module))

   ##  Loading a configuration file. "config" directory is hardcoded    
    def loadConfig(self, fileName, path):
        if path == '':
            path = 'configs'
        else:
            path = 'configs.' + path
        env_context = __import__(path, globals(), locals(), fileName, -1)  
        return env_context.__dict__[fileName].config
    
    def getEnvSpecificConfig(self): 
        return self.loadConfig('env_' + self.configs["envName"], '')

    def getOrgSpecificConfig(self): 
        return self.loadConfig('master_config', '')  
  
    def getProjectpecificConfig(self): 
        return self.loadConfig('project_config', '')    
    
    def getModuleSpecificConfig(self, moduleName): 
        return self.loadConfig(moduleName, 'modules')    
 
    def getEnvSpecificModuleConfig(self, moduleName): 
        return self.loadConfig(moduleName, self.configs["envName"])
        
    def get_conf(self):
        return str(self.configs)
```

The update function merges the content of the dictionaries in a recursive manner. This provides proper overwrite of colliding items.

```python

import collections

def update(d, u):
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            r = update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d
```

The snippet below demonstrate how to initialize and use the ConfigContext helper class. It requires the name of the current module and it reads the 'envName' value from the context.properties dictionary.
After the initialization the cc.configs dictionary contains the aggregated properties.

```python

from helper import config_merger

def GenerateConfig(context):
  
  module = "frontend"
  cc = config_merger.ConfigContext(context.properties, module)
  return {
      'resources': [], 
      'outputs': [{
          'name': 'env_name',
          'value': context.properties["envName"]
      },{
          'name': 'context',
          'value': cc.configs['CONTEXT']
      },{
          'name': 'HQ_Address',
          'value': cc.configs['HQ_Address']
      },{
          'name': 'ServiceName',
          'value': cc.configs['ServiceName']
      },{
          'name': 'versionNR',
          'value': cc.configs['versionNR']
      },{
          'name': 'outp_3',
          'value':str(cc.configs)
      }]
     
  }
```


