from ruamel.yaml import YAML
import sys

class DMConfig:
    yaml = YAML()
    
    def __init__(self, resources):
        self.imports = set([])
        self.out = {}
        self.out["resources"] = []
        for res in resources:
            if res.dm_api[-3:] == ".py" or  res.dm_api[-6:] == ".jinja":
                self.imports.add(res.dm_api)
            self.out["resources"].append(res.base_yaml)
            
        self.out["imports"]=[]
        for item in self.imports:
            self.out["imports"].append({'path' : item})

        self.yaml_dump()
        
    def yaml_dump(self):
        self.yaml.dump(self.out, sys.stdout)