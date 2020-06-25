"""Creates a tpu and gives it read rights on the given storage bucket."""


def GenerateConfig(context):
  """GenerateConfig returns the deployment manager config."""
  project = context.env['project']
  zone = context.properties['zone']
  tpu_name = 'tpu-%s' % context.env['deployment']
  accelerator_type = (
      context.properties['acceleratorType']
      if 'acceleratorType' in context.properties else 'v2-8')
  tensorflow_version = (
      context.properties['tensorflowVersion']
      if 'tensorflowVersion' in context.properties else '1.8')
  cidr_block = context.properties['cidrBlock']
  resources = []
  resources.append({
      'name': tpu_name,
      'type': 'gcp-types/tpu-v1alpha1:projects.locations.nodes',
      'properties': {
          'nodeId': tpu_name,
          'parent': 'projects/%s/locations/%s' % (project, zone),
          'acceleratorType': accelerator_type,
          'network': context.properties.get('network') or 'default',
          'cidrBlock': cidr_block,
          'tensorflowVersion': tensorflow_version,
      }
  })
  gcs_bucket = context.properties.get('gcsBucket')
  if gcs_bucket:
    resources.append({
        'name': 'get-iam-policy',
        'action': 'gcp-types/storage-v1:storage.buckets.getIamPolicy',
        'properties': {
            'bucket': gcs_bucket,
            'userProject': project,
        }
    })
    resources.append({
        'name': 'add-iam-policy',
        'action': 'gcp-types/storage-v1:storage.buckets.setIamPolicy',
        'properties': {
            'bucket': gcs_bucket,
            'userProject': project,
            'policy': '$(ref.get-iam-policy)',
            'gcpIamPolicyPatch': {
                'add': [{
                    'roles':
                        'roles/storage.objectViewer',
                    'members': [
                        'serviceAccount:$(ref.%s.serviceAccount)' % tpu_name
                    ]
                }]
            }
        }
    })
  return {'resources': resources}
