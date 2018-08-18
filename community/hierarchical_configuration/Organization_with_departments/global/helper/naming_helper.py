class NamingHelper:
    configs = {}

    def __init__(self, context):
        self.configs = context.configs

    def getProjectName(self, name):
        return self.configs['Org_level_configs']['Org_Short_Name'] + '-' + self.configs['Department_level_configs']['Department_Short_Name'] + '-' + name + '-' + self.configs["envName"]
