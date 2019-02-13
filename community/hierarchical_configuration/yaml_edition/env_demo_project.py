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

from helper import config_merger


def GenerateConfig(context):
    """Main entry point for Deployment Manager logic"""

    module = "frontend"
    cc = config_merger.ConfigContext(context, module)

    return {
        'resources': [
            #{
            #'name': 'simple_frontend',
            #'type': 'simple_frontend.py',
            #'properties': context.properties
        #}
        ],
        'outputs': [{
            'name': 'env_name',
            'value': context.properties["envName"]
        }, {
            'name': 'context',
            'value': cc.configs['CONTEXT']
        }, {
            'name': 'HQ_Address',
            'value': cc.configs['HQ_Address']
        }, {
            'name': 'ServiceName',
            'value': cc.configs['ServiceName']
        }, {
            'name': 'versionNR',
            'value': cc.configs['versionNR']
        }, {
            'name': 'outp_3',
            'value': str(cc.configs)
        }]
    }
