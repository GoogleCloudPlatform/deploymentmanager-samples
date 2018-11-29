# App Engine

This template creates a Google App Engine's App and Version resource.

## Prerequisites

- Install [gcloud](https://cloud.google.com/sdk)
- Create a [GCP project, set up billing, enable requisite APIs](../project/README.md)
- Enable the App Engine Admin API and either the App Engine Flexible Environment API or the App Engine Standard Environment API based on your choice of environment.
- Grant the [appengine.appAdmin](https://cloud.google.com/appengine/docs/admin-api/access-control) and [OWNER](https://cloud.google.com/appengine/docs/standard/python/access-control#primitive_roles) IAM roles to the [Deployment Manager service account](https://cloud.google.com/deployment-manager/docs/access-control#access_control_for_deployment_manager)
- Please refer to the [App Engine Overview](https://cloud.google.com/appengine/docs/standard/python/an-overview-of-app-engine)
  for information regarding the structure of an App Engine application

## Deployment

### Resources

- [gcp-types/appengine-v1:appengine.apps.create](https://cloud.google.com/appengine/docs/admin-api/reference/rest/v1/apps)
- [appengine.v1.version](https://cloud.google.com/appengine/docs/admin-api/reference/rest/v1/apps.services.versions)

### Properties

See the `properties` section in the schema file(s):

-  [App Engine](app_engine.py.schema)
-  [App Engine Version](app_engine_service.py.schema)


### Usage

1. Clone the [Deployment Manager samples repository](https://github.com/GoogleCloudPlatform/deploymentmanager-samples)

    ```shell
        git clone https://github.com/GoogleCloudPlatform/deploymentmanager-samples
    ```

2. Go to the [community/cloud-foundation](../../) directory

    ```shell
        cd community/cloud-foundation
    ```

3. Copy the example DM config to be used as a model for the deployment, in this
   case [examples/app_engine.yaml](examples/app_engine.yaml)

    ```shell
        cp templates/app_engine/examples/app_engine.yaml \
            my_app_engine.yaml
    ```

4. Change the values in the config file to match your specific GCP setup.
   Refer to the properties in the schema files described above.

    ```shell
        vim my_app_engine.yaml  # <== change values to match your GCP setup
    ```

5. Create your deployment as described below, replacing <YOUR_DEPLOYMENT_NAME>
   with your with your own deployment name

    ```shell
        gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
            --config my_app_engine.yaml
    ```

`Note:` Once created, this deployment cannot be deleted. There is currently no
way to delete an existing app in Google Application Engine. Also, the app
settings cannot be changed once the app had been created. The only way to
delete the application is to [shut down the project](https://cloud.google.com/appengine/docs/standard/python/console/?csw=1#delete_app).

## Examples

- [App Engine](examples/app_engine.yaml)
- [Standard App Engine Environment](examples/standard_app_engine.yaml)
- [Flexible App Engine Environment](examples/flexible_app_engine.yaml)
