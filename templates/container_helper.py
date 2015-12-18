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
"""Helper methods for working with containers in config."""
import common
import default
import yaml

# Specific properties for this component, also see container_instance
DCKRENV = default.DCKRENV
DCKRIMAGE = default.DCKRIMAGE

MANIFEST = """
version: v1beta2
containers:
  - name: %(name)s
    image: %(dockerImage)s
    ports:
      - name: %(name)s-port
        hostPort: %(port)i
        containerPort: %(port)i
    %(env)s
"""


def GenerateManifest(context):
  """Generates a Container Manifest given a Template context.

  Args:
    context: Template context, which must contain dockerImage and port
        properties, and an optional dockerEnv property.

  Returns:
    A Container Manifest as a YAML string.
  """
  env = ""
  env_list = []
  if DCKRENV in context.properties:
    for key, value in context.properties[DCKRENV].iteritems():
      env_list.append({"name": key, "value": value})
  if env_list:
    env = "env: " + yaml.dump(env_list, default_flow_style=True)

  manifest_yaml_string = MANIFEST % {
      "name": context.env["name"],
      "dockerImage": context.properties[DCKRIMAGE],
      "port": context.properties[default.PORT],
      "env": env
  }
  return common.GenerateEmbeddableYaml(manifest_yaml_string)
