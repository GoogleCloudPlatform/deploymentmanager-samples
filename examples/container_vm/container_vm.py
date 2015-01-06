#Copyright 2014 Google Inc. All rights reserved.
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.

#% description: Creates a Container VM with the provided Container manifest.
#% parameters:
#% - name: zone
#%   type: string
#%   description: Zone in which this VM will run
#%   required: true
#% - name: containerImage
#%   type: string
#%   description: Name of the Google Cloud Container VM Image
#%     (e.g., container-vm-v20140731).
#%   required: true
#% - name: containerManifest
#%   type: string
#%   description: String containing the Container Manifest in YAML
#%   required: true

"""Creates a Container VM with the provided Container manifest.
"""

import yaml


def GenerateConfig(context):
  # Loading the container manifest into a YAML object model so that it will be
  # serialized as a single JSON-like object when converted to string.
  manifest = yaml.load(context.imports[context.properties["containerManifest"]])

  return """
resources:
  - type: compute.v1.instance
    name: %(name)s
    properties:
      zone: %(zone)s
      machineType: https://www.googleapis.com/compute/v1/projects/%(project)s/zones/%(zone)s/machineTypes/n1-standard-1
      metadata:
        items:
          - key: google-container-manifest
            value: "%(manifest)s"
      disks:
        - deviceName: boot
          type: PERSISTENT
          boot: true
          autoDelete: true
          initializeParams:
            diskName: %(name)s-disk
            sourceImage: https://www.googleapis.com/compute/v1/projects/google-containers/global/images/%(containerImage)s
      networkInterfaces:
        - accessConfigs:
            - name: external-nat
              type: ONE_TO_ONE_NAT
          network: https://www.googleapis.com/compute/v1/projects/%(project)s/global/networks/default
""" % {"name": context.env["name"] + "-" + context.env["deployment"],
       "project": context.env["project"],
       "zone": context.properties["zone"],
       "containerImage": context.properties["containerImage"],
       "manifest": manifest}
