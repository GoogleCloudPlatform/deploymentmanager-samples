# Generating DM config from live resources

## Overview
`genconfig.py` allows you to snapshot a set of live GCP resources into a
Deployment Manager Jinja template so that you can repeatably deploy those
resources or share their configuration with others.

The tool takes a project, a file containing a list of resource `selfLinks`,
and an optional output directory, in which three files will be generated. If no
output directory is specified, it will use the current directory.

**NOTE**: `genconfig.py` requires that gcloud be locally available and properly
configured to work.

## Using genconfig

### Resource links

The main input to `genconfig` is a file containing resource URLs. These URLs
must be the `selfLink` URL from the Cloud resource itself, and can be found with
one of the following methods:

* gcloud: fetch the full YAML form of the desired resource. An example command:
  `gcloud compute instances describe my-instance --format yaml`
* Equivalent REST: look up the equivalent JSON form of the desired resource in
  the Cloud Console. At the bottom of the resource details page, click the
  "Equivalent REST" link.

`genconfig` supports both the full path format and the shortened format:

* https://www.googleapis.com/compute/v1/projects/my-project/zones/us-central1-f/instanceGroupManagers/test
* projects/my-project/zones/us-central1-f/instanceGroupManagers/test

Store the resource URLs, one per line, in a text file for input.

### Call genconfig

For usage information, call `genconfig` with no parameters.

```
./genconfig.py
```

`genconfig` takes the project in which the resources live, the filename
containing the resources, and an optional output directory. The output director
defaults to the current working directory.

```
./genconfig.py my-project resources.txt output/
```

This will result in the following generated files:

* `config.yaml`: a simple top level config which instantiates the generated
  template.
* `generated.jinja`: the generated template containing the resource definitions.
* `generated.jinja.schema`: the schema for the generated template.

### Customization

The generated Jinja template has parameterized the project in the configuration,
but you may want to do some more customization.

Currently, `genconfig` does not fill in resource relationships, so be sure to
add references between resources that have dependencies.

For example, an Instance Group Manager which depends on an Instance Template
will be generated with a link,

```
instanceTemplate: https://www.googleapis.com/compute/v1/projects/{{env['project']}}/global/instanceTemplates/my-instance-template
```

but you may need to add a reference so it deploys in the correct order.

```
instanceTemplate: $(ref.my-instance-template.selfLink)
```

You may also want to add more parameterization to your new template, like which
zone the resources are deployed to, or VM size. For more information, see the
documentation on [using templates](https://cloud.google.com/deployment-manager/configuration/adding-templates)
and [using schemas](https://cloud.google.com/deployment-manager/configuration/using-schemas).

## Example

### Deploy

First deploy the [HA Service
example](https://github.com/GoogleCloudPlatform/deploymentmanager-samples/tree/master/examples/v2/ha-service).
This will create a load balanced autoscaled managed instance group to work with.

```
gcloud deployment-manager deployments create ha \
  --config ha-service/example.yaml
```

### Run genconfig

Fill in the appropriate resource URLs. See this [example
input](example/resources.txt).

Now run `genconfig` to generate the new templates.

```
./genconfig.py <project> example/resources.txt generated/
```

### Post-processing

After generating the new template, be sure to add references between the
resources to ensure proper deployment ordering. See this [example
output](example/generated.jinja).

### Redeploy

Before redeploying, delete the old resources and deployment.

```
gcloud deployment-manager deployments delete ha
```

Now you can redeploy using the new configurations.

```
gcloud deployment-manager deployments create ha --config example/config.yaml
```

## Known Issues

* Only supports compute resources right now.
* Does not add references between resources.
* Does not work with Compute Instances, as they do not retain some important
  input parameters as part of the Instance object (namely, static vs. ephemeral
  IP, and InitializationParams for boot disk).
