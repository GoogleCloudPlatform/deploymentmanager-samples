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