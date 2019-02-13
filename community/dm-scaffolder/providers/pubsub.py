"""
PubSubTopic provider implements GCP PubSub Topic specific transaltions
Supports V1, CFT versions
"""
import providers.baseprovider as base


### PubSub Subscription start ###

class PubSubSubscriptionBase(base.BaseProvider):
    """
    Common implementation shared accross all PubSub Subscription versions.
    This class should not be used outside of it's child classes.
    """

    def __init__(self, dm_api, gcloud_stage, gcloud_flags=''):
        base.BaseProvider.__init__(
            self, "pubsub", "subscriptions", dm_api, gcloud_stage, gcloud_flags)

    def get_new(self):
        return None  # not supposed to run


class PubSubSubscriptionV1(PubSubSubscriptionBase):
    """ PubSub-topic V1 API provider"""

    def __init__(self, gcloud_flags=''):
        PubSubSubscriptionBase.__init__(
            self, "gcp-types/pubsub-v1:projects.subscriptions", "", gcloud_flags)

    def get_new(self):
        return PubSubSubscriptionV1()


class PubSubSubscriptionCFT(PubSubSubscriptionBase):
    """ PubSub-Subscription CFT API provider - DO NOT USE DIRECTLY"""

    def __init__(self, gcloud_flags=''):
        PubSubSubscriptionBase.__init__(
            self, "../templates/pubsub/pubsub.py", " ", gcloud_flags)

    def get_new(self):
        return PubSubSubscriptionCFT()

    def fill_properties(self):
        self.base_yaml['properties']['topic'] = self.properties['topic'] 
        self.base_yaml['properties']['subscriptions'] = [ self.properties]

### PubSub Subscription end ###

### PubSub Topics start ###

class PubSubTopicBase(base.BaseProvider):
    """
    Common implementation shared accross all PubSub Topic versions.
    This class should not be used outside of it's child classes.
    """

    def __init__(self, dm_api, gcloud_stage, gcloud_flags=''):
        base.BaseProvider.__init__(
            self, "pubsub", "topics", dm_api, gcloud_stage, gcloud_flags)

    def get_new(self):
        return None  # not supposed to run


class PubSubTopicV1(PubSubTopicBase):
    """ PubSub-topic V1 API provider"""

    def __init__(self, gcloud_flags=''):
        PubSubTopicBase.__init__(
            self, "gcp-types/pubsub-v1:projects.topics", "", gcloud_flags)

    def get_new(self):
        return PubSubTopicV1()


class PubSubTopicCFT(PubSubTopicBase):
    """ PubSub-topic CFT API provider """

    def __init__(self, gcloud_flags=''):
        PubSubTopicBase.__init__(
            self, "../templates/pubsub/pubsub.py", " ", gcloud_flags)

    def get_new(self):
        return PubSubTopicCFT()

    def fill_properties(self):
        self.base_yaml['properties']['topic'] = self.properties
        self.base_yaml['properties']['subscriptions'] = []
        self.get_subscriptions()

    def get_subscriptions(self):
        """ Sub-optimal implementation """

        __subscriptions = PubSubSubscriptionCFT().get_list()
        __subs_yaml = []
        for sub in __subscriptions:
            if sub.base_yaml['properties']['topic'] == self.base_yaml['properties']['topic']['name']:
                 __subs_yaml.append(sub.base_yaml['properties']['subscriptions'][0])
        self.base_yaml['properties']['subscriptions'] = __subs_yaml
