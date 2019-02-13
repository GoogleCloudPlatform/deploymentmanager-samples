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

""" Provider classes for GCP Folders"""
import sys

import providers.baseprovider as base


class FolderBase(base.BaseProvider):
    """ Common implementation of Folder APIs"""

    folder_readonly_properties = [
        "createTime",
        "lifecycleState"]

    def __init__(self, dm_api, gcloud_stage, gcloud_flags=''):
        self.readonly_properties += self.folder_readonly_properties
        base.BaseProvider.__init__(
            self, "resource-manager", "folders", dm_api, gcloud_stage, gcloud_flags)

    def get_new(self):
        """ Virtual class to return a new instane of the matching provider class"""
        raise NotImplementedError('subclasses must override get_new()!')

    def get_list(self, gcloud_flags=""):
        return self.get_list_by_parent(" --organization=" + self.config.configs['organization_id'] + " " + gcloud_flags, 0)

    def get_list_by_parent(self, parent, level):
        """ List of the folders under a specific parent node."""

        folders = []
        folders_tmp = super(FolderBase, self).get_list(parent)
        if level < 4:
            for folder in folders_tmp:
                folders.append(folder)
                folders += self.get_list_by_parent(" --folder=" +
                                                   folder.properties["name"][8:], level+1)
        return folders

    def get_folder_ids(self, forced_update=False):
        """ Return all folder IDs under the ORG recursively"""

        folder_ids = self.config.configs['folders_list_cache']
        if forced_update or len(folder_ids) == 0:
            folder_ids=[]
            for folder in self.get_list():
                folder_ids.append(folder.properties["name"][8:])
            self.config.update_folders(folder_ids)
            
        return folder_ids

class FolderAlpha(FolderBase):
    """ Folder Alpha API provider"""

    def __init__(self, gcloud_flags=''):
        FolderBase.__init__(
            self, "gcp-types/cloudresourcemanager-v2:folders", "alpha ", gcloud_flags)

    def get_new(self):
        return FolderAlpha()


class FolderCFT(FolderBase):
    """ Folder CFT API provider"""

    def __init__(self, gcloud_flags=''):
        FolderBase.__init__(
            self, "../templates/folder/folder.py", "alpha ", gcloud_flags)

    def get_new(self):
        return FolderCFT()

    def fill_properties(self):
        self.base_yaml['properties']['folders'] = [self.properties]
