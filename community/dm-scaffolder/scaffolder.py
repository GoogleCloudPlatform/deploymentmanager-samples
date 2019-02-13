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

""" running the scaffolder examples """

from dm_config import DMConfig
from providers.firewall import FirewallCFT
from providers.folder   import FolderCFT
from providers.project  import ProjectCFT
from providers.network  import NetworkCFT
from providers.pubsub   import PubSubTopicCFT

#DMConfig(FolderCFT().get_list())
#DMConfig(ProjectCFT().get_list())
#DMConfig(NetworkCFT().get_list())
#DMConfig(FirewallCFT().get_list("--project=cft-test-workspace-221111"))
#DMConfig(PubSubTopicCFT().get_list("--project=cft-test-workspace-221111"))
