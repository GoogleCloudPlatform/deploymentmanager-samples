#% description: Creates an autoscaled Instance Group Manager running the
#% specified Docker image.
#% parameters:
#% - name: zone
#%   type: string
#%   description: Zone in which this VM will run
#%   required: true
#% - name: instanceTemplate
#%   type: string
#%   description: URL for the instance template to use for IGM
#%   required: true
#% - name: dockerImage
#%   type: string
#%   description: Name of the Docker image to run (e.g., username/nodejs).
#%   required: true
#% - name: port
#%   type: int
#%   description: Port to expose on the container as well as on the load
#%     balancer (e.g., 8080).
#%   required: false
#% - name: service
#%   type: string
#%   description: Name of the service the port exposes for loadbalancing
#%     (backendService) purposes.
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

"""Creates autoscaled, network LB IGM running specified docker image."""

# Defaults
SIZE_KEY = "size"
DEFAULT_SIZE = 1

MAX_SIZE_KEY = "maxSize"
DEFAULT_MAX_SIZE = 1


def GenerateConfig(context):
  """Generate YAML resource configuration."""

  # Set up some defaults if the user didn't provide any
  if SIZE_KEY not in context.properties:
    context.properties[SIZE_KEY] = DEFAULT_SIZE
  if MAX_SIZE_KEY not in context.properties:
    context.properties[MAX_SIZE_KEY] = DEFAULT_MAX_SIZE

  # NOTE: Once we can specify the port/service during creation of IGM,
  # we will wire it up here.
  return """
resources:
  - name: %(name)s-igm
    type: compute.v1.instanceGroupManager
    properties:
      zone: %(zone)s
      targetSize: %(size)s
      baseInstanceName: %(name)s-instance
      instanceTemplate: %(instanceTemplate)s

  - name: %(name)s-as
    type: compute.v1.autoscaler
    properties:
      zone: %(zone)s
      target: $(ref.%(name)s-igm.selfLink)
      autoscalingPolicy:
        maxNumReplicas: %(maxSize)d
""" % {"name": context.env["name"],
       "zone": context.properties["zone"],
       "port": context.properties["port"],
       "service": context.properties["service"],
       "instanceTemplate": context.properties["instanceTemplate"],
       SIZE_KEY: context.properties[SIZE_KEY],
       MAX_SIZE_KEY: context.properties[MAX_SIZE_KEY]}
