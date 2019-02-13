"""
Subnet provider implements GCP Subnet specific transaltions
Supports V1, CFT versions
"""
import providers.baseprovider as base


class SubnetworkBase(base.BaseProvider):
    """
    Common implementation shared accross all Subnet versions.
    This class should not be used outside of it's child classes.
    """

    Subnetwork_readonly_properties = [
        "kind",
        "fingerprint",
        "x_gcloud_bgp_routing_mode",
        "x_gcloud_subnet_mode"]

    def __init__(self, dm_api, gcloud_stage, gcloud_flags=''):
        
        self.readonly_properties += self.Subnetwork_readonly_properties

        base.BaseProvider.__init__(
            self, "compute", "networks subnets", dm_api, gcloud_stage, gcloud_flags)

    def get_new(self):
        return None  # not supposed to run

class SubnetworkV1(SubnetworkBase):
    """ Subnetwork V1 API provider"""

    def __init__(self, gcloud_flags=''):
        SubnetworkBase.__init__(
            self, "gcp-types/compute-v1:Subnetworks", "", gcloud_flags)

    def get_new(self):
        return SubnetworkV1()

class SubnetworkCFT(SubnetworkBase):
    """ Firewall-rules CFT API provider"""

    def __init__(self, gcloud_flags=''):
        SubnetworkBase.__init__(
            self, "../templates/Subnetworks/Subnetwork.py", " ", gcloud_flags)

    def get_new(self):
        return SubnetworkCFT()
