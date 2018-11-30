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

"""Resource Util Template."""
import yaml

context = None
type_mappings = None
resources = []


class Resource(object):
  """Wrapper for compute resources."""

  def __init__(self, name, resource_type, prop):
    self.name = name + '-' + context.env['deployment']
    self.type = resource_type
    if resource_type in type_mappings:
      self.type = type_mappings[resource_type]
    self.properties = prop
    resources.append(self)

  def Ref(self, prop_name):
    return '$(ref.%s.%s)' % (self.name, prop_name)

  def SelfLink(self):
    return self.Ref('selfLink')

  def __setitem__(self, name, value):
    self.properties[name] = value

  def __getitem__(self, name):
    return self.properties[name]

class ComputeResource(Resource):
  """Wrapper for compute resources."""

  def __init__(self, name, compute_collection, prop):
    prefix = 'gcp-types/compute-' + context.properties['computeVersion'] + ':'
    Resource.__init__(self, name, prefix + compute_collection, prop)


def Resources():
  object_array = []
  for item in resources:
    object_array.append({
        'name': item.name,
        'type': item.type,
        'properties': item.properties
    })
  return {'resources': object_array}


def SetContext(outer_context):
  global context
  global type_mappings
  context = outer_context
  if 'typeMappings.yaml' in context.imports:
    type_mappings = yaml.load(context.imports['typeMappings.yaml'])
  else:
    type_mappings = {}
