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
"""Python template for creating an SSL Certificate."""


def GenerateConfig(ctx):
  """Reads SSL certificate and key from a file."""
  ssl = {'name': '-'.join([ctx.env['deployment'],
                           ctx.env['name'],
                           'ssl']),
         'type': 'compute.v1.sslCertificate',
         'properties': {
             'certificate': '\n'.join([ctx.imports[ctx.properties['crt']],
                                       ctx.imports[ctx.properties['csr']]]),
             'privateKey': ctx.imports[ctx.properties['key']]}}
  return {'resources': [ssl]}

