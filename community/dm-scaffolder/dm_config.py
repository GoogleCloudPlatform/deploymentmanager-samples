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
