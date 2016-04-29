# Copyright 2015 Google Inc. All rights reserved.
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
"""Creates an Instance VM with common defaults."""
# pylint: disable=g-import-not-at-top
import copy
import common
import default

# Properties for this component
BOOTDISKTYPE = default.BOOTDISK
BOOTDISKSIZE = default.BOOTDISKSIZE
CAN_IP_FWD = default.CAN_IP_FWD
DEVIMAGE = 'devImage'
DISK = default.DISK
DISKTYPE = default.DISKTYPE
DISK_RESOURCES = default.DISK_RESOURCES
ENDPOINT_NAME = default.ENDPOINT_NAME
INSTANCE_NAME = default.INSTANCE_NAME
MACHINETYPE = default.MACHINETYPE
METADATA = default.METADATA
NETWORK = default.NETWORK
SUBNETWORK = default.SUBNETWORK
NO_SCOPE = default.NO_SCOPE
PROJECT = default.PROJECT
PROVIDE_BOOT = default.PROVIDE_BOOT
SERVICE_ACCOUNTS = default.SERVICE_ACCOUNTS
SRCIMAGE = default.SRCIMAGE
TAGS = default.TAGS
ZONE = default.ZONE
AUTODELETE_BOOTDISK = 'bootDiskAutodelete'
STATIC_IP = 'staticIP'
NAT_IP = 'natIP'

# Defaults used for modules that imports this one
DEFAULT_DISKTYPE = 'pd-standard'
DEFAULT_IP_FWD = False
DEFAULT_MACHINETYPE = 'n1-standard-1'
DEFAULT_NETWORK = 'default'
DEFAULT_PROVIDE_BOOT = True
DEFAULT_BOOTDISKSIZE = 10
DEFAULT_AUTODELETE_BOOTDISK = True
DEFAULT_STATIC_IP = False
DEFAULT_DATADISKSIZE = 500
DEFAULT_ZONE = 'us-central1-f'
DEFAULT_PERSISTENT = 'PERSISTENT'
DEFAULT_SERVICE_ACCOUNT = [{
    'email': 'default',
    'scopes': [
        'https://www.googleapis.com/auth/cloud.useraccounts.readonly',
        'https://www.googleapis.com/auth/devstorage.read_only',
        'https://www.googleapis.com/auth/logging.write',
        'https://www.googleapis.com/auth/monitoring.write',
    ]
}]

# Set Metadata Value
ATTACHED_DISKS = 'ATTACHED_DISKS'

# Used for SSD special treatment
SCRATCH = 'SCRATCH'


def MakeVMName(context):
  """Generates the VM name."""
  name = context.env['name']
  prop = context.properties
  named = INSTANCE_NAME in prop
  return prop[INSTANCE_NAME] if named else common.AutoName(name,
                                                           default.INSTANCE)


def GenerateComputeVM(context):
  """Generates one VM instance resource."""
  prop = context.properties
  boot_disk_type = prop.setdefault(BOOTDISKTYPE, DEFAULT_DISKTYPE)
  prop[default.DISKTYPE] = boot_disk_type
  can_ip_fwd = prop.setdefault(CAN_IP_FWD, DEFAULT_IP_FWD)
  disks = prop.setdefault(default.DISKS, list())
  local_ssd = prop.setdefault(default.LOCAL_SSD, 0)
  # Temporary alternative while multiple disks on creation is not allowed
  if disks:
    new_disks = prop.setdefault(default.DISK_RESOURCES, list())
    disks, prop[DISK_RESOURCES] = GenerateDisks(context, disks, new_disks)
  machine_type = prop.setdefault(MACHINETYPE, DEFAULT_MACHINETYPE)
  metadata = prop.setdefault(METADATA, dict())
  network = prop.setdefault(NETWORK, DEFAULT_NETWORK)
  vm_name = MakeVMName(context)
  provide_boot = prop.setdefault(PROVIDE_BOOT, DEFAULT_PROVIDE_BOOT)
  tags = prop.setdefault(TAGS, dict([('items', [])]))
  zone = prop.setdefault(ZONE, DEFAULT_ZONE)
  static_ip = prop.get(STATIC_IP, DEFAULT_STATIC_IP)
  nat_ip = prop.get(NAT_IP, None)
  if provide_boot:
    dev_mode = DEVIMAGE in prop and prop[DEVIMAGE]
    src_image = common.MakeC2DImageLink(prop[SRCIMAGE], dev_mode)
    boot_name = common.AutoName(context.env['name'], default.DISK, 'boot')
    disk_size = prop.get(BOOTDISKSIZE, DEFAULT_BOOTDISKSIZE)
    disk_type = common.MakeLocalComputeLink(context, DISKTYPE)
    autodelete = prop.get(AUTODELETE_BOOTDISK, DEFAULT_AUTODELETE_BOOTDISK)
    disks = PrependBootDisk(disks, boot_name, disk_type, disk_size, src_image,
                            autodelete)
  if local_ssd:
    disks = AppendLocalSSDDisks(context, disks, local_ssd)
  machine_type = common.MakeLocalComputeLink(context, default.MACHINETYPE)
  network = common.MakeGlobalComputeLink(context, default.NETWORK)
  subnetwork = ''
  if default.SUBNETWORK in prop:
    subnetwork = common.MakeSubnetworkComputeLink(context, default.SUBNETWORK)

  # To be consistent with Dev console and gcloud, service accounts need to be
  #  explicitly disabled
  remove_scopes = prop[NO_SCOPE] if NO_SCOPE in prop else False
  if remove_scopes and SERVICE_ACCOUNTS in prop:
    prop.pop(SERVICE_ACCOUNTS)
  else:  # Make sure there is a default service account
    prop.setdefault(SERVICE_ACCOUNTS, copy.deepcopy(DEFAULT_SERVICE_ACCOUNT))

  resource = []
  access_config = {'name': default.EXTERNAL, 'type': default.ONE_NAT}

  if static_ip and nat_ip:
    raise common.Error(
        'staticIP=True and natIP cannot be specified at the same time')
  if static_ip:
    address_resource, nat_ip = MakeStaticAddress(vm_name, zone)
    resource.append(address_resource)
  if nat_ip:
    access_config['natIP'] = nat_ip

  network_interfaces = []
  if subnetwork:
    network_interfaces.insert(0, {
        'network': network,
        'subnetwork': subnetwork,
        'accessConfigs': [access_config]
    })
  else:
    network_interfaces.insert(0, {
        'network': network,
        'accessConfigs': [access_config]
    })

  resource.insert(0, {
      'name': vm_name,
      'type': default.INSTANCE,
      'properties': {
          'zone': zone,
          'machineType': machine_type,
          'canIpForward': can_ip_fwd,
          'disks': disks,
          'networkInterfaces': network_interfaces,
          'tags': tags,
          'metadata': metadata,
      }
  })

  # Pass through any additional property to the VM
  if SERVICE_ACCOUNTS in prop:
    resource[0]['properties'].update({SERVICE_ACCOUNTS: prop[SERVICE_ACCOUNTS]})
  return resource


def MakeStaticAddress(vm_name, zone):
  """Creates a static IP address resource; returns it and the natIP."""
  address_name = vm_name + '-address'
  address_resource = {
      'name': address_name,
      'type': default.ADDRESS,
      'properties': {
          'name': address_name,
          'region': common.ZoneToRegion(zone),
      },
  }
  return (address_resource, '$(ref.%s.address)' % address_name)


def PrependBootDisk(disk_list, name, disk_type, disk_size, src_image,
                    autodelete):
  """Appends the boot disk."""
  # Request boot disk creation (mark for autodelete)
  boot_disk = [{
      'autoDelete': autodelete,
      'boot': True,
      'deviceName': name,
      'initializeParams': {
          'diskType': disk_type,
          'diskSizeGb': disk_size,
          'sourceImage': src_image
      },
      'type': DEFAULT_PERSISTENT,
  }]
  return boot_disk + disk_list


def AppendLocalSSDDisks(context, disk_list, num_of_local_ssd):
  """Apends local ssds."""
  project = context.env[default.PROJECT]
  prop = context.properties
  zone = prop.setdefault(ZONE, DEFAULT_ZONE)
  local_ssd_disks = []
  for i in range(0, num_of_local_ssd):
    local_ssd_disks.append({
        'deviceName': 'local-ssd-%s' % i,
        'type': SCRATCH,
        'interface': 'SCSI',
        'mode': 'READ_WRITE',
        'autoDelete': True,
        'initializeParams': {'diskType': common.LocalComputeLink(
            project, zone, 'diskTypes', 'local-ssd')}
    })
  return disk_list + local_ssd_disks


def GenerateDisks(context, disk_list, new_disks):
  """Generates as many disks as passed in the disk_list."""
  project = context.env[default.PROJECT]
  prop = context.properties
  zone = prop.setdefault(ZONE, DEFAULT_ZONE)
  sourced_disks = []
  disk_names = []
  for disk in disk_list:
    d_name = (disk[default.DEVICE_NAME] if default.DISK_NAME not in disk else
              disk[default.DISK_NAME])
    d_autodelete = (True if default.AUTO_DELETE not in disk else
                    disk[default.AUTO_DELETE])
    d_type = (DEFAULT_PERSISTENT if default.TYPE not in disk else
              disk[default.TYPE])

    if default.DISK_SOURCE in disk:  # Existing disk, expect disk api link
      source = disk[default.DISK_SOURCE]
    elif d_type == SCRATCH:  # No special treatment needed for SSD disk
      if default.INITIALIZEP in disk:
        disk_type = disk[default.INITIALIZEP][DISKTYPE]
      else:
        disk_type = 'local-ssd'
      disk[default.INITIALIZEP] = {DISKTYPE: common.LocalComputeLink(
          project, zone, 'diskTypes', disk_type)}
      sourced_disks.append(disk)
      continue
    else:
      if default.DEVICE_NAME not in disk and default.DISK_NAME not in disk:
        raise common.Error('deviceName or diskName is needed for each disk in '
                           'this module implemention of multiple disks per vm.')
      # In the Instance API reference, size and type are within this property
      if default.INITIALIZEP in disk:
        disk_init = disk[default.INITIALIZEP]
        disk_size = disk_init.setdefault(default.DISK_SIZE,
                                         DEFAULT_DATADISKSIZE)
        passed_disk_type = disk_init.setdefault(DISKTYPE, DEFAULT_DISKTYPE)
      # You can also simply pass the size and type properties directly
      else:
        disk_size = disk.setdefault(default.DISK_SIZE, DEFAULT_DATADISKSIZE)
        passed_disk_type = disk.setdefault(DISKTYPE, DEFAULT_DISKTYPE)
      disk_type = common.LocalComputeLink(project, zone, 'diskTypes',
                                          passed_disk_type)
      new_disks.append({
          'name': d_name,
          'type': default.DISK,
          'properties': {
              'type': disk_type,
              'sizeGb': disk_size,
              'zone': zone
          }
      })  # pyformat: disable
      disk_names.append(d_name)
      source = common.Ref(d_name)
    sourced_disks.append({
        'deviceName': d_name,
        'autoDelete': d_autodelete,
        'boot': False,
        'source': source,
        'type': d_type,
    })

  items = prop[METADATA].setdefault('items', list())
  items.append({'key': ATTACHED_DISKS, 'value': ','.join(disk_names)})
  return sourced_disks, new_disks


def AddServiceEndpointIfNeeded(context):
  """If the endpoint property is present, it will add a service endpoint."""
  prop = context.properties
  if ENDPOINT_NAME not in prop:
    return []
  network = common.MakeGlobalComputeLink(context, default.NETWORK)
  reference = '$(ref.' + MakeVMName(context) + '.name)'
  address = common.MakeFQHN(context, reference)
  name = prop[ENDPOINT_NAME]
  resource = [
      {
          'name': name,
          'type': default.ENDPOINT,
          'properties': {
              'addresses': [
                  {'address': address}
              ],
              'dnsIntegration': {
                  'networks': [network]
              }
          }
      }
  ]
  return resource


def GenerateResourceList(context):
  """Returns list of resources generated by this module."""
  resources = GenerateComputeVM(context)
  resources += common.AddDiskResourcesIfNeeded(context)
  resources += AddServiceEndpointIfNeeded(context)
  return resources


def GenerateOutputList(unused_context, resource_list):
  """Returns list of outputs generated by this module."""
  vm_res = resource_list[0]
  outputs = [{
      'name': 'ip',
      'value': ('$(ref.%s.networkInterfaces[0].accessConfigs[0].natIP)' %
                vm_res['name']),
  }]
  return outputs


@common.FormatErrorsDec
def GenerateConfig(context):
  """Generates YAML resource configuration."""
  resource_list = GenerateResourceList(context)
  output_list = GenerateOutputList(context, resource_list)
  return common.MakeResource(resource_list, output_list)
