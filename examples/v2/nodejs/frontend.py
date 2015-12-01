#% description: Creates an autoscaled, network load-balanced Instance Group
#%   Manager running the specified Docker image.
#% parameters:
#% - name: zone
#%   type: string
#%   description: Zone in which this VM will run
#%   required: true
#% - name: dockerImage
#%   type: string
#%   description: Name of the Docker image to run (e.g., username/mysql).
#%   required: true
#% - name: port
#%   type: int
#%   description: Port to expose on the container as well as on the load
#%     balancer (e.g., 8080).
#%   required: false
#% - name: size
#%   type: int
#%   description: Initial size of the Managed Instance Group. If omitted,
#%     defaults to 1
#%   required: false
#% - name: maxSize
#%   type: int
#%   description: Maximum size the Managed Instance Group will be autoscaled to.
#%     If omitted, defaults to 1
#%   required: false
#% - name: containerImage
#%   type: string
#%   description: Image of the container to run the container in (for example)
#%     container-vm-v20150317
#%     If omitted, defaults to: container-vm-v20150317
#%   required: false
#% - name: dockerEnv
#%   type: map
#%   description: Map of key-value pairs that will be exported to container
#%      as env variables.
#%   required: false

"""Creates autoscaled, network LB IGM running specified docker image."""

# Defaults
SIZE_KEY = "size"
DEFAULT_SIZE = 1

MAX_SIZE_KEY = "maxSize"
DEFAULT_MAX_SIZE = 1

CONTAINER_IMAGE_KEY = "containerImage"
DEFAULT_CONTAINER_IMAGE = "container-vm-v20151103"

DOCKER_ENV_KEY = "dockerEnv"
DEFAULT_DOCKER_ENV = "{}"


def GenerateConfig(context):
  """Generate YAML resource configuration."""

  # Set up some defaults if the user didn't provide any
  if SIZE_KEY not in context.properties:
    context.properties[SIZE_KEY] = DEFAULT_SIZE
  if MAX_SIZE_KEY not in context.properties:
    context.properties[MAX_SIZE_KEY] = DEFAULT_MAX_SIZE
  if CONTAINER_IMAGE_KEY not in context.properties:
    context.properties[CONTAINER_IMAGE_KEY] = DEFAULT_CONTAINER_IMAGE
  if DOCKER_ENV_KEY not in context.properties:
    context.properties[DOCKER_ENV_KEY] = DEFAULT_DOCKER_ENV

  # Pull the region out of the zone
  region = context.properties["zone"][:context.properties["zone"].rfind("-")]

  return """
resources:
  - name: %(name)s
    type: container_instance_template.py
    properties:
      port: %(port)d
      dockerEnv: %(dockerEnv)s
      dockerImage: %(dockerImage)s
      containerImage: %(containerImage)s

  - name: %(name)s-igm
    type: compute.v1.instanceGroupManager
    properties:
      zone: %(zone)s
      targetSize: %(size)s
      targetPools: [$(ref.%(name)s-tp.selfLink)]
      baseInstanceName: %(name)s-instance
      instanceTemplate: $(ref.%(name)s-it.selfLink)

  - name: %(name)s-as
    type: compute.v1.autoscaler
    properties:
      zone: %(zone)s
      target: $(ref.%(name)s-igm.selfLink)
      autoscalingPolicy:
        maxNumReplicas: %(maxSize)d

  - name: %(name)s-hc
    type: compute.v1.httpHealthCheck
    properties:
      port: %(port)d
      requestPath: /_ah/health

  - name: %(name)s-tp
    type: compute.v1.targetPool
    properties:
      region: %(region)s
      healthChecks: [$(ref.%(name)s-hc.selfLink)]

  - name: %(name)s-lb
    type: compute.v1.forwardingRule
    properties:
      region: %(region)s
      portRange: %(port)d
      target: $(ref.%(name)s-tp.selfLink)

""" % {"name": context.env["name"],
       "zone": context.properties["zone"],
       "region": region,
       SIZE_KEY: context.properties[SIZE_KEY],
       MAX_SIZE_KEY: context.properties[MAX_SIZE_KEY],
       "port": context.properties["port"],
       "dockerImage": context.properties["dockerImage"],
       DOCKER_ENV_KEY: context.properties[DOCKER_ENV_KEY],
       CONTAINER_IMAGE_KEY: context.properties[CONTAINER_IMAGE_KEY]}
