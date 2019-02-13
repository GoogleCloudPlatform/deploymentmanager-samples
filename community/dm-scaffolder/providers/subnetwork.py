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
