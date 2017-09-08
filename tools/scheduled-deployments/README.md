# Scheduled Deployments

## Overview

Scheduled Deployments enable easy creation and deletion of deployment resources
in [Google Cloud Deployment
Manager](https://cloud.google.com/deployment-manager/docs/) on a custom
schedule.

After a one-time setup, you can easily specify resource deployment and cleanup
on a preset schedule within a configuration file. Each Scheduled Deployment can
have a number of Triggers, whose schedules are defined with a cron expression.
An active Trigger announces either the creation/update or deletion of a
deployment configuration. An App Engine cron job dictates periodic checks every
10 minutes to look for active Triggers.

Scheduled Deployments integrate functionality from Cloud Functions, App Engine,
Pub/Sub, Datastore, and Cloud Storage. They are designed to be simple, reliable,
and scalable.

### Example use cases

-   Customers are mostly business users, so a company would like to shut down
    most of their servers between 7pm and 5am to cut costs.
-   A team regularly receives a large dataset to process every Tuesday morning,
    so they need to schedule a batch processing job.
-   A business is launching a new product on a specified day and want their
    infrastructure to go live at a certain time.

## Walkthrough

### 1 Setup

Prepare an App Engine app with a Cron job, a Pub/Sub topic, source files for two
Cloud Functions, a Scheduled Deployment composite type, and specification for a
type provider.

#### 1.1 Prerequisites

-   Install the [Google Cloud SDK](https://cloud.google.com/sdk/)
-   [Enable project
    billing](https://support.google.com/cloud/answer/6293499#enable-billing)
-   [Enable the following APIs in your
    project](https://console.cloud.google.com/apis/library):
    -   Google Cloud Deployment Manager V2 API
    -   Google Cloud Functions API
    -   Google Cloud Pub/Sub API
    -   Google Cloud Storage

#### 1.2 Download the Scheduled Deployments directory

You can clone the Deployment Manager samples repository and navigate to the
tools/scheduled_deployments directory.

```sh
$ https://github.com/GoogleCloudPlatform/deploymentmanager-samples.git
```

#### 1.3 Upload zipped Cloud Functions files to Cloud Storage

Create a zipped folder

```sh
$ zip -jr ./functions scheduled-deployments.zip
```

and upload that folder to Cloud Storage

```sh
$ gsutil cp scheduled-deployments.zip gs://[PROJECT-ID].appspot.com
```

where `gs://[PROJECT-ID].appspot.com` is your Cloud Storage bucket name.

#### 1.4 Host the Open API specification at a public URL

In the specification file `openapi.json`, replace the placeholders `[REGION]`,
`[PROJECT-ID]`, and `[ROUTER-FUNCTION-NAME]`.

You may use the bash script `parameters_init.sh` to automatically replace these
fields. For example:

```sh
$ ./parameters_init.sh --project [PROJECT-ID] --region us-central1 --function_name sd-router
```

The specification file must be hosted at a publicly-available URL, such as on
Cloud Storage. Make sure the file is set to be shared publicly. To upload to
Cloud Storage, you can execute

```sh
$ gsutil cp -a public-read openapi.json gs://[PROJECT-ID].appspot.com
```

so your specification file will be available at
`https://storage.googleapis.com/[PROJECT-ID].appspot.com/openapi.json`.

#### 1.5 Create App Engine app with Cron timer

Follow [this Firebase sample](https://github.com/firebase/functions-cron) to
create an App Engine app with a Cron service that triggers a Pub/Sub topic. You
will not need to create the functions listed here, but you should create a
Pub/Sub topic that the Cron service will trigger:

```sh
gcloud beta pubsub topics create [TOPIC-NAME]
```

### 2 Scheduling - create and modify Scheduled Deployment resources

Deploy Scheduled Deployment resource types. An HTTP-triggered Cloud Function
manages the create, update, and delete requests by maintaining the deployment
details in Datastore.

#### 2.1 Create a Scheduled Deployment sd_template.py type

In your configuration, you must include a Scheduled Deployment template type
resource. The template [`sd_template.py`](./sd_template.py) creates three
resources:

-   a Scheduled Deployment [type
    provider](https://cloud.google.com/deployment-manager/docs/fundamentals#type_providers),
-   an HTTP-triggered Cloud Function that manages Scheduled Deployment
    resources, and
-   a Pub/Sub-triggered Cloud Function that looks for active Triggers and make
    deployments as appropriate.

The required properties for `sd_template.py` are:

-   `region`
-   `project` - project ID
-   `sourceArchiveUrl` - Cloud Storage bucket location of zipped Cloud Functions
    files, e.g. `gs://[PROJECT-ID].appspot.com/scheduled-deployments.zip`
-   `descriptorUrl` - publicly-hosted URL for the type provider specification
    from Step 1.4, e.g.
    `https://storage.googleapis.com/[PROJECT-ID].appspot.com/openapi.json`
-   `schedulingEntryPoint` - name of Cloud Function that manages scheduling,
    `router` by default
-   `deploymentEntryPoint` - name of Cloud Function that manages deployment,
    `deployScheduledDeployments` by default
-   `typeProviderName` - name to use for type provider resource
-   `routerFunctionName` - name to use for router function resource. This must
    match the name specified in your Open API spec.
-   `pubsubTopicName` - name of Pub/Sub topic that the Cron job publishes to

After you have deployed the `sd_template.py` resource, you can create Scheduled
Deployment types in future configurations as long as the type provider still
exists.

#### 2.2 Create Scheduled Deployment resources

After a Scheduled Deployment type provider has been created, you can create
Scheduled Deployment resources in Deployment Manager by specifying their type
as:

```
type: [PROJECT-ID]/[TYPE-PROVIDER-NAME]:/[ROUTER-FUNCTION-NAME]/{name}
```

You can first deploy the Scheduled Deployment `sd_template.py` type and then
specify Scheduled Deployment resources in a separate config. You can also create
Scheduled Deployment resources in the same config, but note that you must list
the Scheduled Deployment resources as dependent on the router Cloud Function. To
[specify
dependencies](https://cloud.google.com/deployment-manager/docs/configuration/create-explicit-dependencies),
add

```
metadata:
  dependsOn:
  - [ROUTER-FUNCTION-NAME]
```

to your Scheduled Deployment resource. The router function name must be
hard-coded in; at the moment, Deployment Manager does not support dependencies
with template types.

Scheduled Deployment resources must contain the following properties:

-   `name` - name to use when making and deleting deployments
-   `user` - this field will eventually be used as an authorization token
-   `description`
-   `triggers` - a list of Trigger entities

Triggers must specify:

-   `name`
-   `description`
-   `type` - always "timer" for Scheduled Deployments
-   `time` - a cron expression
-   `action` - either `CREATE_OR_UPDATE` or `DELETE`

If the action is `CREATE_OR_UPDATE`, the Trigger must also include `config`,
containing contents of a standard Deployment Manager configuration file, and can
optionally specify `importName` and `importContent` to allow one import into the
configuration.

Refer to [`sd_config.yaml`](./sd_config.yaml) for a sample configuration file.

#### 2.2 Deploy configuration

Deploy your configuration by executing

```sh
$ gcloud deployment-manager deployments create [DEPLOYMENT-NAME] --config [CONFIG-FILE]
```

#### 2.3 Update and delete Scheduled Deployments

Make changes to your deployment configuration and to create new Scheduled
Deployments, modify existing ones, or delete others by updating the deployment:

```sh
$ gcloud deployment-manager deployments update [DEPLOYMENT-NAME] --config [CONFIG-FILE]
```

Deleting a deployment will delete all Scheduled Deployments listed along with
resources from the Scheduled Deployment template type:

```sh
$ gcloud deployment-manager deployments delete [DEPLOYMENT-NAME]
```

Deleting a Scheduled Deployment deletes the Scheduled Deployment entities from
Datastore along with their associated Triggers and Operations. However, it does
not delete any associated deployments in Deployment Manager.

### 3 Deployment - check for active Triggers and make deployments

The Cron job alerts a Pub/Sub topic every 10 minutes. A Cloud Function responds
to the Pub/Sub event by retrieving all Scheduled Deployment entities from
Datastore, checking for any active Triggers, and making deployments or deletions
as appropriate. See the "About active Triggers" section for more details.

#### 3.1 Sit back and relax

This work is done for you by the Pub/Sub-triggered Cloud Function!

### 4 Debugging issues - track your Scheduled Deployments

Track deployment activity and success/failure with Cloud Function logs and
Operation resources in Datastore.

#### 4.1 Cloud Functions logs

View Cloud Functions logs on the command line

```sh
$ gcloud beta functions logs read
```

or in the [Cloud Console](https://console.cloud.google.com/logs).

To display only errors, use the flag `--min-log-level=ERROR`.

#### 4.2 Operations in Datastore

Track the Operations created in Datastore. An Operation is created for any
create, update, or delete operation on a Scheduled Deployment regardless of
success or failure. The Operations are specified in the format of [Open API
operation objects](https://swagger.io/specification/#operationObject).

An operation records a successful operation with a 'result' column and an
unsuccessful one with an 'error' column.

#### 4.3 Stackdriver alerts

To more actively monitor your Scheduled Deployments, you can set up [alerts with
Stackdriver Monitoring](https://cloud.google.com/monitoring/alerts/).

## Things to note

### About active Triggers

An active Trigger is one that is scheduled to be deployed at the current cron
job request.

A Trigger is considered active if its schedule falls within half the cron
interval from the current time. With a Cron interval of 10 minutes, a Trigger
must be scheduled between five minutes ago and five minutes in the future to be
called active.

When more than one trigger is active, priority goes to the later of the active
triggers. If multiple triggers have the same active timestamp, priority is given
alphabetically (case-sensitive).

In the spirit of fault-tolerance, the system tracks when a Scheduled Deployment
was last deployed or deleted. If a Trigger's most recent past interval occurred
after the last deployment, it indicates we have missed a deployment. In that
case, that Trigger is considered active even if it is not in the current active
time window. When a Scheduled Deployment is first created, all triggers are
considered active because the system treats all previous intervals as missed.

### Cron expressions

A cron expression is a simple and flexible way to specify repeating time
inverals. It consists of five fields:

1.  minute (0-59)
2.  hour (0-23)
3.  day of month (1-31)
4.  month (1-12 or Jan-Dec)
5.  day of week (0-6 or Sun-Sat)

Any field may also be an asterisk (*), which denotes no specific value. Consider
the examples:

Cron expression | Interpretation
--------------- | --------------------------------------------
`* * * * *`     | every minute (trigger will always be active)
`0 0 * * *`     | every day at midnight
`30 6,18 * * *` | every day at 6:30am and 6:30pm
`0 8 * * 1-5`   | Monday-Friday at 8am
`0 0 1 4 *`     | April 1 at midnight

[Learn more](https://en.wikipedia.org/wiki/Cron#CRON_expression) about cron
expressions. Note that our [cron
parser](https://www.npmjs.com/package/cron-parser) does not currently support
non-standard characters L, W, and #.

Note that all time is in UTC.

### Datastore overview

Scheduled Deployments employs three tables ("kinds") in Datastore:
ScheduledDeployment, Trigger, and Operation. Trigger and Operation entities are
children of ScheduledDeployment entities.

Details provided by a Scheduled Deployment resource type are stored in
ScheduledDeployment and Trigger entities. An Operation entity is created for
every create/update or delete operation performed on a Scheduled Deployment.

### Directory overview

-   `./functions/` - contains files for Cloud Functions
-   `./functions/test/` - contains unit tests for Cloud Functions
-   `./functions/index.js` - defines the two Cloud Functions
-   `./functions/constants.js` - defines constants used throughout Cloud
    Functions
-   `./functions/package.js` - specifies Cloud Functions dependencies
-   `./openapi.json` - defines OpenAPI Specification for a Scheduled Deployments
    type provider
-   `./sd_template.py` - DM template file that specifies a Scheduled Deployments
    composite type
-   `./sd_config.yaml` - sample configuration file
-   `./parameters_init.sh` - script that fill in placeholders in `openapi.json`
    and `sd_config.yaml`

### Constants

-   `PROJECT_ID` - your project ID
-   `PREFIX` - prefix to prepend to Scheduled Deployment names
-   `KIND` - name of the Datastore kind (analogous to a database table) of your
    Scheduled Deployment entities
-   `TRIGGER_KIND` - name of the Datastore kind of your Trigger entities
-   `OPERATION_KIND` - name of the Datastore kind of your Operation entities
-   `CRON_INTERVAL` - how long (in minutes) the cron timer waits between
    triggers. This should match the interval used by the App Engine cron
    service.

### Testing

The Cloud Functions code is tested using [Mocha](https://mochajs.org/) with
[Chai](http://chaijs.com/) and [Sinon](http://sinonjs.org/). To execute the unit
tests, you must have
[npm](https://docs.npmjs.com/getting-started/installing-node) installed. Install
the required npm packages, which are specified as dependencies in
`package.json`. In the `functions` folder, execute

```sh
$ npm install
```

which will download the required libraries into a directory called
`node_modules`. Then, execute

```sh
$ npm test
```

to run all unit tests.


There are two scripts provided for integration tests in the `/tests/` directory. 

To test the Scheduling phase, execute

```sh
$ ./test_scheduling.sh --project [PROJECT_ID]
```

To test the Deployment phase, execute

```sh
$ ./test_deployment.sh --project [PROJECT_ID]
```

You may add a `--debug` flag to either command to display output from all commands.

## Limitations

-   All Scheduled Deployment information is stored in Datastore, which can be
    easily edited by users manually.
-   A configuration file can only have a single import. However, this limitation
    can be worked around with [composite
    types](https://cloud.google.com/deployment-manager/docs/configuration/templates/create-composite-types).
-   Scheduled Deployment configs do not support templates.
-   Datastore caps transaction size at 10 MB, which limits the size of
    configuration files.
-   Cron expressions are those supported by the npm library `cron-parser`, which
    is extensive but [does not
    support](https://github.com/harrisiirak/cron-parser/issues/21) the
    non-standard characters L, W, and #.

## Looking ahead

We can envision Scheduled Deployments eventually supporting the following
features:

-   Unrolling of tar/zip files from Cloud Storage to accomodate extremely large
    configs.
-   Allowing more than one import to be specified.
-   Reap Operation entities in Datastore (perhaps deleting old Operations after
    10 or so accumulate for a given Scheduled Deployment).
-   Additional attempts to create or delete deployments if the first attempted
    failed due to a server error.
-   Careful treatment of sensitive data.

### Coordinated Deployments

Coordinated Deployments are a generalized case of Scheduled Deployments.

This Scheduled Deployments framework can be easily adapted for use with generic
Pub/Sub events instead of a set timer. To do so, you can deploy the
Pub/Sub-triggered Cloud Function and have it subscribe to your desired topic
instead of the timer event. For this, you will need one Cloud Function for each
Coordinated Deployment rather than one master function.

The Cloud Function that checks Triggers and manages deployments is currently
triggered by Pub/Sub events, but could easily be adapted to HTTP requests
instead, which would significantly expand the possible conditions for deployment
creation or deletion.
