# Copyright 2018 Google Inc. All rights reserved.
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

#####################################################################################################
## Credit for in-depth recursive merge:
## https://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth
##
#####################################################################################################

import collections


def update(d, u):
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            r = update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


#####################################################################################################

#####################################################################################################
## ConfigContext class loads and merges the config files in the right order.
##
## Context: In this example this is the name/abrevation of the environment: dev/test/prod. However it
## can be extended with any name like preprod, sandbox, etc.
##
## Module: Module is the actual part of your system which currently need the properties. For example:
## FrontendServer, RabbitMQServer, Networking, CloudSQL, etc. It is a designers choice how granular a
## module should be.
#####################################################################################################

import yaml

class ConfigContext:

    configs = {}
    __context = None

    def __init__(self, context, module):
        self.__context = context
        self.configs.update(context.properties)
        update(self.configs, self.getOrgSpecificConfig())
        update(self.configs, self.getProjectpecificConfig())
        update(self.configs, self.getEnvSpecificConfig())
        update(self.configs, self.getModuleSpecificConfig(module))
        update(self.configs, self.getEnvSpecificModuleConfig(module))

    ##  Loading a configuration file. "config" directory is hardcoded for python files
    ## LoadConfig supports both .py and .yaml files, see ../configs folder
    ## The __init__ function defines the files and their order during the merge process
    def loadConfig(self, fileName, path):
        if path == '':
            py_path = 'configs'
            yaml_path = 'configs'
        else:
            py_path = 'configs.' + path
            yaml_path = 'configs/' + path
        
        env_context = {}
        
        try:
            env_context = __import__(py_path + '.' + fileName, globals(), locals(), fileName, -1)  
            env_context = env_context.config
        except:
            # Proper exception handling needed
            print py_path + '/' + fileName + ".py config file not found"
        try:
            env_context = yaml.load(self.__context.imports[yaml_path + '/' + fileName + '.yaml'])
        except:
            # Proper exception handling needed
            print py_path + '/' + fileName + ".yaml config file not found"

        return env_context

    def getEnvSpecificConfig(self):
        return self.loadConfig(self.configs["envName"], 'envs')

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
