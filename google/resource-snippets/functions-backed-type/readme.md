# Custom Type Provider

## Background

Most resources in Google Cloud can be managed using Deployment Manager.
Resources can be created, updated, deleted as part of the deployments.
Deployment Manager calls CRUD APIs of the corresponding Google Cloud services to
manipulate the resouces.

This works most of the time, however sometimes there is a need to call an API
that is not part of any resource type supported by the Deployment Manager.
Or, sometimes there is a need to execute imperative logic during the deployment and
that cannot be easily modeled in a declarative Deployment Manager configuration.

This example shows one approach to deal with these situations, i.e. how to
create a custom service and call it as part of a deployment.

## Custom Types

The approach in this example is based on custom types. In addition to regular
Google Cloud resources Deployment Manager allows users to create their own custom
resource types. These custom types can be backed by any bespoke service, not just
usual GCP services.

To implement a custom type the user needs to provide an Open API descriptor
for their custom service and then describe method mappings, input mappings,
and auth. After that Deployment manager knows how the APIs in that custom service
map to CRUD operations, and this allows to use this service as a custom resource.

In general, implementing, hosting, and configuring a custom service as a backend for
custom Deployment Manager resource type can be prohibitively hard and expensive.

Google Cloud provides a number of serverless solutions that could reduce the complexity
required to implement such solution.

## High Level Approach

This example shows how to create a custom type that is backed by Cloud Functions.

From high level perspective this implementation works like this:

* Cloud Function:
  * the solution contains a Cloud Function that handles HTTP requests;
  * whenever an HTTP request is received, the Cloud Function executes different logic
    depending on the HTTP verb of the request;
  * during execution this Cloud Function calls other Google Cloud APIs to perform
    resource operations;
* OpenAPI description document:
  * the solution contains an OpenAPI document that describes the contract for the
    Cloud Function;
  * this allows Deployment Manager to understand what HTTP verbs are handled by the
    Cloud Function and what is the format for requests and responses;

When Cloud Function code is ready and OpenAPI doc is written it is time to use them in
a custom resource type:

* the Cloud Function needs to be deployed and reachable;
* OpenAPI doc needs to be hosted at an HTTP endpoint:
  * the doc will need to point to the URL of the deployed function;
* custom type needs to be created either using a `gcloud` command or as part of the
  deployment:
  * the URL to the OpenAPI doc will need to be specified;
* a resource with this custom type can be now specified in a deployment;

## Cloud Function

A Cloud Function that contains the logic to manipulate the desired resource is the
core of the solution. This specific example demostrates how to write a Cloud Function
from scratch that will call Cloud SQL APIs to create, get, patch, and delete a
Cloud SQL instance. The logic is not limited to calling Google Cloud APIs. Cloud Functions
can contain arbitrary code that can implement any desired logic. For example, it is
possible to call other non-GCP services, connect to databases, poll for messages or
check a status of a resource, call multiple APIs during the same request, etc.

The Cloud Function in this example is written in Javascript and is intended to be hosted
in Node10 environment.

### Function Structure

* `function/function.js`:
  * main file for the Cloud Function;
  * contains the entrypoint function that is called when Cloud Function receives an HTTP request;
  * implements logic to check the HTTP verb of the request and execute corresponding logic;
  * implements basic input validation and basic error handling;
  * the logic to handle different HTTP verbs is extracted into separate files for readability, below
* `function/instanceGet.js`:
  * implements logic to call Cloud SQL Admin `get` API that returns an existing SQL instance;
* `function/instanceInsert.js`:
  * implements logic to call Cloud SQL Admin `insert` API that creates a new SQL instance;
* `function/instancePatch.js`:
  * implements logic to call Cloud SQL Admin `patch` API that returns an existing SQL instance;
* `function/instanceGet.js`:
  * implements logic to call Cloud SQL Admin `delete` API that returns an existing SQL instance;
* `function/googleApiHelper.js`:
  * a small helper module to set up the Google API client, speficially to configure auth;
* `function/package.json`:
  * node.js package manifest, describes the application, specifies the dependencies;
  * this example only uses a `googleapis` library to talk to Google Cloud APIs but other libraries
    can be added as dependencies;

Note that there are some limitations with Cloud Functions that can make this approach not work for
some use cases:

* Cloud Functions run sandboxed, they can't keep local state, some language APIs are not available;
* only some languages and runtimes are available, it's impossible to run an arbitrary language
  runtime as a Cloud Function;
* allowed function execution time is limited. By default max allowed Function exeuction time is 1 min.
  It can be set to up to 9 min during function deployment. If function doesn't finish in that time it
  will be terminated with a timeout error;

### Function Deployment

In order to deploy a function you can use these commands:

```
cd function
gcloud functions deploy CLOUD_FUNCTION_NAME --source=. --set-env-vars=GCP_PROJECT=YOUR_GCP_PROJECT
```

Replace `CLOUD_FUNCTION_NAME` with a URL-friendly name for the function. It will be used in the URL for
the function, e.g. `https://example-region-example-project.cloudfunctions.net/CLOUD_FUNCTION_NAME`. Note
that you need to replace `CLOUD_FUNCTION_NAME` in `package.json` and in `api.json` with your function
name as well.

Replace `YOUR_GCP_PROJECT` with your GCP project ID. Starting from Node10 environment Cloud Functions
are unable to detect the current project they're deployed in. Since this example uses the information
about the current project we need to pass it to the function as an environment variable during deployment.

Instead of running a `gcloud` command to deploy a Function there are alternatives that are not
shown in this example, they are described in the public documentation for Deployment manager and
Cloud Functions:

* you can upload a zip with the source code for the Cloud Function and then deploy it by
  creating a resource with type `gcp-types/cloudfunctions-v1:projects.locations.functions` in the
  Deployment Manager configuration;
* you can open Cloud Console UI in the web browser and create a function from there either by
  pointing to the sources zip or by manually pasting the source code;

## OpenAPI Doc

OpenAPI description doc allows Deployment Manager to map CRUD operations for the new custom type to
the Cloud Function invocations. Deployment Manager maps the HTTP verbs that are described in the doc
to CRUD operations and populates the inputs according to the schema described in the doc.

Few things to note in `api.json` for this example:

* uses the URL of the deployed Cloud Function;
* describes one collection by the name `CLOUD_FUNCTION_NAME` and a path parameter;
* the collection supports `get`, `post`, `put`, `delete` verbs;
* schemas are defined for inputs and outputs of the operations;

This OpenAPI doc needs to be deployed to a publicly accessible HTTP endpoint. It could be protected by HTTP basic auth.

When creating a custom resource type in Deployment Manager based on the OpenAPI doc, Deployment Manager will:

* map HTTP verbs to CRUD operations to model the resource lifecycle;
* populate the inputs and outputs based on schemas in the doc;
* will call the Cloud Function URL specified in the doc, using different methods for different lifecycle states;

### Using OpenAPI doc to create a Custom Type

In this example the custom type is created as part of the deployment.
In `cloud-sql-type-deployment.yaml` there is a custom type specified as as resource, it needs to point at
the public URL where the OpenAPI desrcription doc is available at:

```
- name: cloud-sql-custom-type
  type: deploymentmanager.local.typeProvider
  properties:
    descriptorUrl: https://OPEN_API_DOC_URL
```

## Using the Custom Type

In the `cloud-sql-type-deployment.yaml` example deployment you can see a couple of things happening:

* a custom type is created based on the OpenAPI doc that descibes how to call the Cloud Function;
  ```
  resources:

  - name: cloud-sql-custom-type
    type: deploymentmanager.local.typeProvider
    properties:
      descriptorUrl: https://OPEN_API_DOC_URL
  ```

* a resource is created that uses that custom type;

  ```
  - name: custom-sql-instance-name
    type: YOUR_GCP_PROJECT/cloud-sql-custom-type:/CLOUD_FUNCTION_NAME/{instance}
    properties:
      instance: custom-test-instance-name
      name: custom-test-instance-name
      settings:
        tier: db-n1-standard-1
    metadata:
      dependsOn:
      - cloud-sql-custom-type
  ```
* a resource descibes a few properties that Deployment Manager will map to the inputs and pass to the
  Function during deployment. Function will read these properties and pass them to GCP APIs to create
  Cloud SQL instance;
* note that resource that uses the type needs a `dependsOn`, so that Deployment Manager waits until the
  custom type is created before using it;

### Notes

* this example does not show how to configure authentication or IAM policy for the Cloud Function:
  * the function in the example is expected to be publicly accessible via HTTP without authentication:
      * to set up authentication the OpenAPI doc needs to explicitly map the auth token to the input
        header;
      * on top of that Cloud Endpoints can be set up for Cloud Functions for further flexibility
        with auth;
  * the expectation is that the service account used by the Function has permissions to perform all
    operations on Cloud SQL instances:
      * setting up permissions for the service account is outside of the scope of this example;
* this example calles Cloud SQL APIs to create SQL instances, there are few things to note:
  * Cloud SQL doesn't allow to re-use the instance names for a few days. So if you delete an instance
    you can't create another one with the same name;
  * Cloud SQL instance creation takes a few minutes:
    * the example doesn't wait until instance is fully operational, it reports success as soon as
      provisioning is started;
    * if there's an attempt to modify the instance before it has finished provisioning the operation
      will fail;
    * if necessary, in situations like this extra polling logic may be added to the function to monitor
      the status of the resource and only report successful creation after provisioning has finished;
* this example logs a lot of debug information. In production scnarios all logging needs to be reviewed
  in order not to log any information that is not intended for logging;
