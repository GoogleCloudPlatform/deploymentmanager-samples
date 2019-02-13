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

""" Provider classes for GCP Project"""
import providers.baseprovider as base
import sys
from subprocess import check_output

class ProjectBase(base.BaseProvider):
    """ Common implementation of Project APIs"""

    project_readonly_properties = [
        "createTime"]

    def __init__(self, dm_api, gcloud_stage, gcloud_flags=''):
        
        self.host_projects = []
        self.guest_projects = {}
        self.readonly_properties += self.project_readonly_properties

        base.BaseProvider.__init__(self, "", "projects", dm_api, gcloud_stage, gcloud_flags)
    def get_new(self):
        """ Virtual class to return a new instane of the matching provider class"""
        raise NotImplementedError('subclasses must override get_new()!')


    def get_list(self, gcloud_flags=""):
        
        projects_tmp = super(ProjectBase, self).get_list(gcloud_flags)
        projects_list=[]
        for project in projects_tmp:
            if project.properties['lifecycleState'] == "ACTIVE":
                project.properties.pop('lifecycleState', None)
                projects_list.append(project)
        self.get_vpc_host_project_ids()
        self.get_vpc_guest_project_ids()

        return projects_list

    def set_cft_defaults(self):
        self.base_yaml['properties']['removeDefaultVPC'] = True
        self.base_yaml['properties']['removeDefaultSA'] = True

    def get_vpc_host_project_ids(self):
        
        use_shell = sys.platform == 'win32'
        props = check_output(("gcloud compute shared-vpc organizations list-host-projects " + self.config.configs['organization_id'] + " --format yaml" ).split(), shell=use_shell).split('---')
        
        for prop in props:
            if prop is None:
                continue
            prop = self.yaml.load(prop)
            if prop is None:
                continue
            self.host_projects.append(prop['name'])

    def get_vpc_guest_project_ids(self):

        for id in self.host_projects:
            
            use_shell = sys.platform == 'win32'
            try:
                props = check_output(("gcloud compute shared-vpc associated-projects list " + id + " --format yaml" ).split(), shell=use_shell).split('---')
                
                for prop in props:
                    if prop is None:
                        continue
                    prop = self.yaml.load(prop)
                    if prop is None:
                        continue
                    
                    self.guest_projects[prop['id']] = id
            except:
                print "Project " + id + "can't be reached. Potentially up for deletion."

    def set_as_vpc_host(self):
        #Not implemented by default
        return None

    def set_as_vpc_guest(self, host_id):
        #Not implemented by default
        return None

class ProjectV1(ProjectBase):
    """ Project V1 API provider"""

    def __init__(self, gcloud_flags=''):
        ProjectBase.__init__(
            self, "gcp-types/cloudresourcemanager-v1:projects", "", gcloud_flags)

    def get_new(self):
        return ProjectV1()


class ProjectCFT(ProjectBase):
    """ Project CFT API provider"""

    def __init__(self, gcloud_flags=''):
        ProjectBase.__init__(
            self, "../templates/project/project.py", "", gcloud_flags)

    def get_new(self):
        return ProjectCFT()

    def set_as_vpc_host(self):
        self.base_yaml['properties']['sharedVPCHost'] = True
        
    def set_as_vpc_guest(self, host_id):
        self.base_yaml['properties']['sharedVPC'] = host_id
        
    def get_list(self, gcloud_flags=""):
        
        projects_list = super(ProjectCFT, self).get_list(gcloud_flags)
        
        for project in projects_list:
            project.set_cft_defaults()
            if project.properties['projectId'] in self.host_projects:
                project.set_as_vpc_host()
            elif project.properties['projectId'] in self.guest_projects:
                project.set_as_vpc_guest(self.guest_projects[project.properties['projectId']])
            
            use_shell = sys.platform == 'win32'
            props = self.yaml.load(check_output(("gcloud beta billing projects describe " + project.properties['projectId'] + " --format yaml" ).split(), shell=use_shell))
            project.base_yaml['properties']['billingAccountId'] = props.get('billingAccountName')
            
        return projects_list
