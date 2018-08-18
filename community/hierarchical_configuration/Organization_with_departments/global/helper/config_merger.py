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


class ConfigContext:

    configs = {}

    def __init__(self, context, module):
        self.configs.update(context)
        update(self.configs, self.getOrgSpecificConfig())
        update(self.configs, self.getProjectpecificConfig())
        update(self.configs, self.getSystempecificConfig())
        update(self.configs, self.getEnvSpecificConfig())
        update(self.configs, self.getModuleSpecificConfig(module))
        update(self.configs, self.getEnvSpecificModuleConfig(module))

        #############################################################################################
        ## #Old version .update() only adds or replaces values in the dictionary on the first level.
        ## self.configs.update(self.getOrgSpecificConfig())
        ## self.configs.update(self.getProjectpecificConfig())
        ## self.configs.update(self.getEnvSpecificConfig())
        ## self.configs.update(self.getModuleSpecificConfig(module))
        ## self.configs.update(self.getEnvSpecificModuleConfig(module))
        #############################################################################################

    ##  Loading a configuration file. "config" directory is hardcoded
    def loadConfig(self, fileName, path):
        if path == '':
            path = 'configs'
        else:
            path = 'configs.' + path
        env_context = __import__(path + '.' + fileName, globals(), locals(),
                                 fileName, -1)
        return env_context.config

    def getEnvSpecificConfig(self):
        return self.loadConfig(self.configs["envName"], 'envs')

    def getOrgSpecificConfig(self):
        return self.loadConfig('org_config', '')

    def getProjectpecificConfig(self):
        return self.loadConfig('department_config', '')

    def getSystempecificConfig(self):
        return self.loadConfig('system_config', '')

    def getModuleSpecificConfig(self, moduleName):
        return self.loadConfig(moduleName, 'modules')

    def getEnvSpecificModuleConfig(self, moduleName):
        return self.loadConfig(moduleName, self.configs["envName"])

    def get_conf(self):
        return str(self.configs)
