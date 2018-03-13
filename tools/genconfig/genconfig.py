#!/usr/bin/env python
#
# Copyright 2016 Google Inc. All rights reserved.
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

"""Generates a Jinja template from a list of GCE resource URLs."""

from __future__ import print_function
from copy import deepcopy
import re
from subprocess import check_output
import sys
import yaml


# pylint: disable=line-too-long
SELF_LINK_PATTERN = re.compile(r'.*/([^/]+/[^/]+)/projects/([^/]+)/(.+)/([^/]+)/(.*)$')
COMPUTE_SELF_LINK_PATTERN = re.compile(r'projects/([^/]+)/(.+)/([^/]+)/(.*)$')


def usage():
  print(''.join(['Usage: ', sys.argv[0],
                 ' <project> <resource URL file> [<output dir>]']),
        file=sys.stderr)
  print('  Default output dir is current directory.', file=sys.stderr)
  print(file=sys.stderr)
  print('  Will generate the following files:', file=sys.stderr)
  print('    - <output dir>/generated.jinja', file=sys.stderr)
  print('    - <output dir>/generated.jinja.schema', file=sys.stderr)
  print('    - <output dir>/config.yaml', file=sys.stderr)


def get_config(urls, project):
  """Given a set of resource URLs, returns a DM config.

  The DM config will contain a resource for each URL provided, filled with the
  appropriate type and properties from the live resource.

  All instances of the specified project will be replaced with
  "{{ env['project'] }}".

  Args:
    urls: the list of resource URLs to process into config
    project: the project for the associated resources

  Returns:
    A valid DM config containing all resources from the URL list.

  Raises:
    Exception: if any URLs or resources are invalid.
  """

  resources = []
  for cmd in get_gcloud_cmds(urls, project):
    if not cmd:
      continue

    useShell = sys.platform == 'win32'
    props = check_output(cmd.split(), shell=useShell)
    resources.extend(get_resource_config(props, project, urls))

  return {'resources': resources}


def get_resource_config(pstr, project, urls):
  """Returns a list of DM resource configurations.

  The algorithm for this is:

  1) Load resource properties into YAML
  2) Move name into the resource name field
  3) Map kind to DM type
  4) Scrub properties of output-only fields from the API
  5) Fill resource properties with scrubbed properties

  Args:
    pstr: the string blob of resource properties to be converted to resource
      config.
    project: the project of the associated resource, used for parameterization

  Returns:
    A list of valid DM configuration for this resource and any auxiliary
    resources.
  """

  for url in urls:
    if url.startswith('projects'):
      url = "https://www.googleapis.com/compute/v1/" + url
    m = SELF_LINK_PATTERN.match(url)
    name = m.group(5)
    ref = "$(ref." + name + ".selfLink)"
    pstr = pstr.replace(url, ref)
  pstr = pstr.replace(project, "{{env['project']}}")
  props = yaml.load(pstr)

  return get_resource_config_from_dict(props)


def get_resource_config_from_dict(props):
  """Helper for get_resource_config()."""

  check_field(props, 'name')
  check_field(props, 'kind')

  resources = [{
      'name': props['name'],
      'type': get_type(props['kind'], props),
      'properties': scrub_properties(props)
  }]

  if props['kind'] == 'compute#instanceGroupManager' and 'autoscaler' in props:
    resources.extend(get_resource_config_from_dict(props['autoscaler']))

  return resources


def scrub_properties(orig_props):
  """Scrubs fields in API object properties for use in DM properties.

  Scrubbed fields include:

  - output-only fields common for most resources
  - output-only fields specific to a particular resource type

  Args:
    orig_props: the resource properties that need to be scrubbed

  Returns:
    The final scrubbed resource properties.
  """

  props = deepcopy(orig_props)

  # Scrub output-only and unnecessary fields that we know about.
  props.pop('name', None)
  props.pop('id', None)
  props.pop('creationTimestamp', None)
  props.pop('status', None)
  props.pop('selfLink', None)

  # Some fields are at multiple layers and need to be scrubbed recursively.
  scrub_sub_properties(props)

  # Scrub fields that some types return.
  scrub_type_specific_properties(props)

  # Location is always returned as a full resource URL, but only the name is
  # used on input.
  if 'zone' in props:
    props['zone'] = props['zone'].rsplit('/', 1)[1]
  if 'region' in props:
    props['region'] = props['region'].rsplit('/', 1)[1]

  return props


def scrub_type_specific_properties(props):
  """Scrubs fields that are unique to certain types."""

  # TargetPool specific stuff.
  props.pop('instances', None)

  # ForwardingRule specific stuff.
  props.pop('IPAddress', None)

  # IGM specific stuff.
  props.pop('currentActions', None)
  props.pop('instanceGroup', None)
  props.pop('autoscaler', None)

  # Instance specific stuff.
  props.pop('cpuPlatform', None)
  props.pop('labelFingerprint', None)

  # Clear all IP assignments from network interfaces. Especially in
  # accessConfigs, where it is assumed there is a static IP address with the
  # given IP if assigned.
  if 'networkInterfaces' in props:
    for i in props['networkInterfaces']:
      i.pop('networkIP', None)
      if 'accessConfigs' in i:
        for ac in i['accessConfigs']:
          # This currently cannot support user-provided static IP, only allows
          # for ephemeral.
          ac.pop('natIP', None)


def scrub_sub_properties(props):
  """Scrubs certain fields that may exist at any level in properties."""
  if isinstance(props, list):
    # May be list of objects, must go deeper.
    for p in props:
      scrub_sub_properties(p)

  if isinstance(props, dict):
    # Scrub properties on this set.
    props.pop('kind', None)
    props.pop('fingerprint', None)

    # Check any sub structures.
    for unused_k, p in props.iteritems():
      scrub_sub_properties(p)


def get_type(kind, props):
  """Converts API resource 'kind' to a DM type.

  Only supports compute right now.

  Args:
    kind: the API resource kind associated with this resource, e.g.,
      'compute#instance'

  Returns:
    The DM type for this resource, e.g., compute.v1.instance

  Raises:
    Exception: if the kind is invalid or not supported.
  """

  parts = kind.split('#')
  if len(parts) != 2:
    raise Exception('Invalid resource kind: ' + kind)

  service = {
      'compute': 'compute.v1'
  }.get(parts[0], None)

  if service is None:
    raise Exception('Unsupported resource kind: ' + kind)

  if parts[1] == 'instanceGroupManager' and 'region' in props:
    return service + '.' + 'regionInstanceGroupManager'

  return service + '.' + parts[1]


def check_field(props, field):
  if field not in props:
    raise Exception(''.join(['Resource properties missing field "',
                             field, '": ',
                             yaml.dump(props, default_flow_style=False)]))


def get_gcloud_cmds(urls, project):
  """Returns list of gcloud describe commands given list of resource URLs."""
  return [get_describe_cmd(u.rstrip(), project) for u in urls]


def get_describe_cmd(url, project):
  r"""Builds a gcloud describe command given a resource URL.

  gcloud command will look like:

    gcloud compute instances describe instance-name \
        --zone us-central1-f --format yaml

  NOTE: only supports compute resources right now.

  Args:
    url: the URL for this resource.
    project: the project of this resource.

  Returns:
    The gcloud command to be used to describe the resource in YAML, or empty
    if no command.

  Raises:
    Exception: if URL is bad.
  """

  m = SELF_LINK_PATTERN.match(url)
  if m:
    service = m.group(1)
    unused_project = m.group(2)
    location = m.group(3)
    collection = m.group(4)
    name = m.group(5)
  else:
    # May be a truncated selfLink, allowed for compute.
    m = COMPUTE_SELF_LINK_PATTERN.match(url)
    if not m:
      raise Exception('Resource URL must be selfLink: ' + url)

    # Assumed truncated selfLink is compute only.
    service = 'compute/v1'
    location = m.group(2)
    collection = m.group(3)
    name = m.group(4)

  if service != 'compute/v1':
    raise Exception(''.join(['!!! Found resource that is unsupported: ', url]))

  # Autoscalers have no associated gcloud command for describing.
  if collection == 'autoscalers':
    print(''.join(['!!! Found autoscaler resource ',
                   name,
                   ', will attempt to generate config from its associated ',
                   'instanceGroupManager (NOTE: you must include the '
                   'associated instanceGroupManager in the resource list).']),
          file=sys.stderr)
    return ''

  return ' '.join(['gcloud compute',
                   get_gcloud_command_group(collection),
                   'describe',
                   name,
                   get_location_flag(location, url, collection),
                   '--format yaml',
                   '--project', project])


def get_gcloud_command_group(collection):
  """Converts API collection to gcloud sub-command group.

  Most collections are a direct mapping, but some are multi-word or have custom
  sub-command groups and must be special-cased here.

  Args:
    collection: collection within the respective API for this resource.

  Returns:
    gcloud command group string for this resource's collection.
  """

  return {
      'backendServices': 'backend-services',
      'backendBuckets': 'backend-buckets',
      'firewalls': 'firewall-rules',
      'forwardingRules': 'forwarding-rules',
      'httpHealthChecks': 'http-health-checks',
      'httpsHealthChecks': 'https-health-checks',
      'instanceTemplates': 'instance-templates',
      'instanceGroupManagers': 'instance-groups managed',
      'targetHttpProxies': 'target-http-proxies',
      'targetHttpsProxies': 'target-https-proxies',
      'targetPools': 'target-pools',
      'urlMaps': 'url-maps',
	  'healthChecks': 'health-checks',
      'instanceGroups': 'instance-groups'
  }.get(collection, collection)


def get_location_flag(location, url, collection):
  """Location flag for gcloud command based on location in URL."""

  # Location will typically be 'global', 'zones/<zone>', or regions/<region>.
  # We will assume the presence of a slash denotes one of the latter two.
  parts = location.split('/')
  if len(parts) > 1:
    if parts[0] == 'zones':
      return ' '.join(['--zone', parts[1]])
    elif parts[0] == 'regions':
      return ' '.join(['--region', parts[1]])

    raise Exception('Invalid location "' + location + '" in URL: ' + url)

  if collection in ['backendServices','forwardingRules']:
    return ' --global'
  # No slash, assume global and so no location flag is needed.
  return ''


def get_config_dot_yaml():
  return {
      'imports': [{
          'path': 'generated.jinja'
      }],
      'resources': [{
          'name': 'generated',
          'type': 'generated.jinja'
      }]
  }


def get_generated_schema():
  return {
      'info': {
          'author': 'Auto-generated template with schema',
          'description': 'Enter description here.',
          'title': 'Enter title here.'
      },
      'properties': {}
  }


def main(argv):
  if len(argv) < 3:
    usage()
    sys.exit(1)

  output_dir = argv[3] if len(argv) == 4 else '.'

  urls = []
  with open(argv[2]) as f:
    urls = [line.rstrip() for line in f]

  config = get_config(urls, argv[1])

  # Write generated template.
  with open(output_dir + '/generated.jinja', 'w') as f:
    f.write(yaml.dump(config, default_flow_style=False))
  with open(output_dir + '/generated.jinja.schema', 'w') as f:
    f.write(yaml.dump(get_generated_schema(), default_flow_style=False))

  # Write yaml config which uses template.
  with open(output_dir + '/config.yaml', 'w') as f:
    f.write(yaml.dump(get_config_dot_yaml(), default_flow_style=False))

  print(''.join(['All done! See files generated in output directory "',
                 output_dir, '".']),
        file=sys.stderr)
  print(file=sys.stderr)
  print(''.join(['You may want to modify them to have different resource names,'
                 , ' parameterized properties,'
                 , ' or references between related resources.']),
        file=sys.stderr)


if __name__ == '__main__':
  main(sys.argv)

