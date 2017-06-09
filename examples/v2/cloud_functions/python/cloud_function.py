# Copyright 2017 Google Inc. All rights reserved.
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
"""Creates a cloud function and calls it."""

import json


def GenerateConfig(context):
  """Generate YAML resource configuration."""
  deployment_name = context.env['deployment']
  function_call = deployment_name + '-function-call'
  function_name = deployment_name + '-function'
  topic_name = deployment_name + '-topic'

  resources = [{
      'name': topic_name,
      'type': 'gcp-types/pubsub-v1:projects.topics',
      'properties': {
          'topic': topic_name,
      }
  }, {
      'type': 'gcp-types/cloudfunctions-v1beta2:projects.locations.functions',
      'name': function_name,
      'properties': {
          'location': context.properties['region'],
          'function': function_name,
          'sourceArchiveUrl': context.properties['sourceArchiveUrl'],
          'entryPoint': context.properties['entryPoint'],
          'eventTrigger': {
              'resource': '$(ref.' + topic_name + '.name)',
              'eventType': 'providers/cloud.pubsub/eventTypes/topic.publish'
          }
      }
  }, {
      'name':
          function_call,
      'action': ('gcp-types/cloudfunctions-v1beta2:'
                 'cloudfunctions.projects.locations.functions.call'),
      'properties': {
          'name': '$(ref.' + function_name + '.name)',
          'data': json.dumps({
              'hola': 'mundo'
          })
      }
  }]
  return {
      'resources':
          resources,
      'outputs': [{
          'name': 'cloud-function-response',
          'value': '$(ref.' + function_call + '.result)'
      }]
  }
