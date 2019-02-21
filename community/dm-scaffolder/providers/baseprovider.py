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
BaseProvider implement common functionalities for all API provider
"""
import sys
import os
from subprocess import check_output
import configs

from ruamel.yaml import YAML


class BaseProvider(object):
    """
    BaseProvider implement common functionalities for all API provider
    """

    readonly_properties = [
        "id",
        "creationTimestamp",
        "status",
        "selfLink"]
    yaml = YAML()

    def __init__(self, base_api, resource, dm_api, gcloud_stage, gcloud_flags=''):
        self.base_api = base_api
        self.gcloud_stage = gcloud_stage
        self.resource = resource
        self.dm_api = dm_api
        self.gcloud_flags = gcloud_flags
        self.base_yaml = {}
        self._set_yaml_base()
        self.properties = {}
        if configs.__file__[-3:] == 'pyc':
            path = configs.__file__[:-4]
        else:
            path = configs.__file__[:-3]
        self.config = configs.Config(path + ".yaml")

    def _set_yaml_base(self):
        """ Setting the YAML wrapper for the DM resource"""

        self.base_yaml['type'] = self.dm_api
        self.base_yaml['name'] = 'not_set'
        self.base_yaml['properties'] = {}

    def yaml_dump(self):
        """ Dumping the providers content in YAML format to String"""
        self.yaml.dump(self.base_yaml, sys.stdout)

    def get_new(self):
        """ Virtual class to return a new instane of the matching provider class"""
        raise NotImplementedError('subclasses must override get_new()!')

    def get_gcloud_command(self):
        """Generating gcloud command based on the provider details"""
        return ("gcloud " + self.gcloud_stage + self.base_api + " " + self.resource +
                " list --format=yaml" + " " + self.gcloud_flags)

    def set_properties(self, _properties):
        """Setting property values for the provider"""
        self.properties = _properties
        self.scrub_properties()

    def fill_properties(self):
        """Filling the porperty and name values for the DM resource based on the provider"""
        self.base_yaml['name'] = self.properties["name"]
        self.base_yaml['properties'] = self.properties

    def get_list(self, gcloud_flags=""):
        """Getting the list of GCP objects and returning them as provider objects"""
        use_shell = sys.platform == 'win32'
        props = check_output((self.get_gcloud_command() +
                              gcloud_flags).split(), shell=use_shell).split('---')
        mylist = []
        for prop in props:
            if prop is None:
                continue
            item = self.get_new()
            prop = self.yaml.load(prop)
            if prop is None:
                continue
            item.set_properties(prop)
            item.fill_properties()
            mylist.append(item)

        return mylist

    def scrub_properties(self):
        """
        Scrubs fields in API object properties for use in DM properties.
        Scrubbed fields include:
        - output-only fields common for most resources
        """

        # Scrub output-only and unnecessary fields that we know about.
        for prop in self.readonly_properties:
            self.properties.pop(prop, None)

        # Some fields are at multiple layers and need to be scrubbed recursively.
        # scrub_sub_properties(props)

        # Scrub fields that some types return.
        # scrub_type_specific_properties(props)

        # Location is always returned as a full resource URL, but only the name is
        # used on input.
        # if 'zone' in props:
        #    props['zone'] = props['zone'].rsplit('/', 1)[1]
        # if 'region' in props:
        #   props['region'] = props['region'].rsplit('/', 1)[1]
