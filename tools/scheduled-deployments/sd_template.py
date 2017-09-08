"""Create resources needed to implement Scheduled Deployments."""


def generate_config(context):
  """Generates configuration."""

  deployment_name = context.env['deployment']
  type_provider_name = context.properties['typeProviderName']
  scheduling_function_name = context.properties['routerFunctionName']
  deployment_function_name = deployment_name + '-deployment'

  type_provider = {
      'name': type_provider_name,
      'type': 'deploymentmanager.v2beta.typeProvider',
      'properties': {
          'descriptorUrl': context.properties['descriptorUrl']
      }
  }

  scheduling_function = {
      'name': scheduling_function_name,
      'type': 'gcp-types/cloudfunctions-v1beta2:projects.locations.functions',
      'properties': {
          'location': context.properties['region'],
          'function': scheduling_function_name,
          'sourceArchiveUrl': context.properties['sourceArchiveUrl'],
          'entryPoint': context.properties['schedulingEntryPoint'],
          'httpsTrigger': {
              'url':
                  ''.join([
                      'https://', context.properties['region'], '-',
                      context.properties['project'], '.cloudfunctions.net/',
                      scheduling_function_name
                  ])
          }
      }
  }

  deployment_function = {
      'name': deployment_function_name,
      'type': 'gcp-types/cloudfunctions-v1beta2:projects.locations.functions',
      'properties': {
          'location': context.properties['region'],
          'function': deployment_function_name,
          'sourceArchiveUrl': context.properties['sourceArchiveUrl'],
          'entryPoint': context.properties['deploymentEntryPoint'],
          'eventTrigger': {
              'resource':
                  'projects/' + context.properties['project'] + '/topics/' +
                  context.pubsubTopicName,
              'eventType':
                  'providers/cloud.pubsub/eventTypes/topic.publish'
          }
      }
  }

  config = {
      'resources': [type_provider, scheduling_function, deployment_function]
  }

  return config
