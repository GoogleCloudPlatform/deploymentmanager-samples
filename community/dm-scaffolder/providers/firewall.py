"""
Firewall provider implements GCP Firewall rule specific transaltions
Supports V1, Beta, CFT versions
"""
import providers.baseprovider as base


class FirewallBase(base.BaseProvider):
    """
    Common implementation shared accross all Firewall versions.
    This class should not be used outside of it's child classes.
    """

    def __init__(self, dm_api, gcloud_stage, gcloud_flags=''):
        base.BaseProvider.__init__(
            self, "compute", "firewall-rules", dm_api, gcloud_stage, gcloud_flags)

    def get_new(self):
        return None  # not supposed to run


class FirewallV1(FirewallBase):
    """ Firewall-rules V1 API provider"""

    def __init__(self, gcloud_flags=''):
        FirewallBase.__init__(
            self, "gcp-types/compute-v1:firewalls", "", gcloud_flags)

    def get_new(self):
        return FirewallV1()


class FirewallBeta(FirewallBase):
    """ Firewall-rules Beta API provider"""

    def __init__(self, gcloud_flags=''):
        FirewallBase.__init__(
            self, "gcp-types/compute-beta:firewalls", "beta ", gcloud_flags)

    def get_new(self):
        return FirewallBeta()


class FirewallCFT(FirewallBase):
    """ Firewall-rules CFT API provider"""

    def __init__(self, gcloud_flags=''):
        FirewallBase.__init__(
            self, "../templates/firewall/firewall.py", "beta ", gcloud_flags)

    def get_new(self):
        return FirewallCFT()

    def fill_properties(self):
        self.base_yaml['properties']['network'] = self.properties.get("network", None)
        self.base_yaml['properties']['rules'] = [self.properties]
