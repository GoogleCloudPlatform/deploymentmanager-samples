"""Creates primary/secondary zone autoscaled IGM running specified container."""

# Defaults
PRIMARY_SIZE_KEY = "primarySize"
DEFAULT_PRIMARY_SIZE = 1

SECONDARY_SIZE_KEY = "secondarySize"
DEFAULT_SECONDARY_SIZE = 0

MAX_SIZE_KEY = "maxSize"
DEFAULT_MAX_SIZE = 1

CONTAINER_IMAGE_KEY = "containerImage"
DEFAULT_CONTAINER_IMAGE = "container-vm-v201500806"

DOCKER_ENV_KEY = "dockerEnv"
DEFAULT_DOCKER_ENV = "{}"


def GenerateConfig(context):
  """Generate YAML resource configuration."""

  # Set up some defaults if the user didn't provide any
  if PRIMARY_SIZE_KEY not in context.properties:
    context.properties[PRIMARY_SIZE_KEY] = DEFAULT_PRIMARY_SIZE
  if SECONDARY_SIZE_KEY not in context.properties:
    context.properties[SECONDARY_SIZE_KEY] = DEFAULT_SECONDARY_SIZE
  if MAX_SIZE_KEY not in context.properties:
    context.properties[MAX_SIZE_KEY] = DEFAULT_MAX_SIZE
  if CONTAINER_IMAGE_KEY not in context.properties:
    context.properties[CONTAINER_IMAGE_KEY] = DEFAULT_CONTAINER_IMAGE
  if DOCKER_ENV_KEY not in context.properties:
    context.properties[DOCKER_ENV_KEY] = DEFAULT_DOCKER_ENV

  return """
resources:
  - name: %(name)s
    type: container_instance_template.py
    properties:
      port: %(port)d
      dockerEnv: %(dockerEnv)s
      dockerImage: %(dockerImage)s
      containerImage: %(containerImage)s

  - name: %(name)s-pri
    type: autoscaled_group.py
    properties:
      zone: %(primaryZone)s
      size: %(primarySize)s
      maxSize: %(maxSize)s
      port: %(port)d
      service: %(service)s
      baseInstanceName: %(name)s-instance
      instanceTemplate: $(ref.%(name)s-it.selfLink)

  - name: %(name)s-sec
    type: autoscaled_group.py
    properties:
      zone: %(secondaryZone)s
      size: %(secondarySize)s
      maxSize: %(maxSize)s
      port: %(port)d
      service: %(service)s
      baseInstanceName: %(name)s-instance
      instanceTemplate: $(ref.%(name)s-it.selfLink)

  - name: %(name)s-hc
    type: compute.v1.httpHealthCheck
    properties:
      port: %(port)d
      requestPath: /_ah/health

  - name: %(name)s-bes
    type: compute.v1.backendService
    properties:
      port: %(port)d
      portName: %(service)s
      backends:
        - name: %(name)s-primary
          group: $(ref.%(name)s-pri-igm.instanceGroup)
        - name: %(name)s-secondary
          group: $(ref.%(name)s-sec-igm.instanceGroup)
      healthChecks: [ $(ref.%(name)s-hc.selfLink) ]

""" % {"name": context.env["name"],
       "primaryZone": context.properties["primaryZone"],
       "secondaryZone": context.properties["secondaryZone"],
       PRIMARY_SIZE_KEY: context.properties[PRIMARY_SIZE_KEY],
       SECONDARY_SIZE_KEY: context.properties[SECONDARY_SIZE_KEY],
       MAX_SIZE_KEY: context.properties[MAX_SIZE_KEY],
       "port": context.properties["port"],
       "service": context.properties["service"],
       "dockerImage": context.properties["dockerImage"],
       DOCKER_ENV_KEY: context.properties[DOCKER_ENV_KEY],
       CONTAINER_IMAGE_KEY: context.properties[CONTAINER_IMAGE_KEY]}
