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

class Config:
    
    yaml = YAML()

    def __init__(self, path):
        self.path = path
        f = open(path, "r")
        self.configs = self.yaml.load(f.read())
        f.close()

    def update_folders(self, folders):
        self.configs['folders_list_cache'] = folders
        print 'lets write'
        with open(self.path, 'w') as yf:
            self.yaml.dump(self.configs, stream=yf)
