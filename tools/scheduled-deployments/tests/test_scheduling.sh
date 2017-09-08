#!/bin/bash
#
# Integration test script for Scheduled Deployments.
#
# Test script creates a Cloud Function, deploys a DM configuration for
# the function, and publishes a message to the corresponding PubSub topic.
# The Cloud Function then adds an entity to Cloud Datastore with details
# about the Scheduled Deployment configuration.

set -e -u

source gbash.sh || exit


###############################################################################
# setup
###############################################################################

DEFINE_string --required project '' 'Project ID to use in test.'
DEFINE_string deployment_file './sample_deployment.json' \
  'Path to .json deployment file.'
DEFINE_string deployment_name 'scheduling-test' \
  'Name of deployment in deployment file.'
DEFINE_string function_name 'scheduling-function' \
  'Name of HTTP-triggered Cloud Function.'
DEFINE_string function_js 'router' \
  'Name of Javascript function to be triggered by Cloud Function.'
DEFINE_string function_path '../functions' \
  'Path to directory containing index.js function.'
DEFINE_string prefix 'sd-' 'Prefix to append to name of deployment resources.'
DEFINE_bool debug --empty_false 'false' \
  'Turn debug mode on, outputting all output from commands.'

gbash::init_google "$@"

prefix="$FLAGS_prefix"
project_id="$FLAGS_project"
project_bucket="gs://$project_id.appspot.com"
deployment_file="$FLAGS_deployment_file"
deployment_name="$FLAGS_deployment_name"
function_js="$FLAGS_function_js"
function_name="${prefix}${FLAGS_function_name}"
function_path="$FLAGS_function_path"

# set debug mode on or off
if [ $FLAGS_debug ]; then
  OUT='/dev/tty'
else
  OUT='/dev/null'
fi

# ensure project ID is valid
if ! gcloud projects describe "$project_id" >/dev/null 2>&1
then
  echo "ERROR: Project ID '$project_id' does not exist, or you do not have " \
    "permission to access it."
  exit 1
fi

# ensure function name is not already used
if gcloud beta functions describe "$function_name" \
  --project "$project_id" >/dev/null 2>&1
then
  echo "ERROR: A function with the name '$function_name' already exists."
  exit 1
fi

# ensure index.js exists in function path
if [[ ! -e "${function_path}/index.js" ]]
then
  echo "ERROR: File 'index.js' does not exist in path '$function_path'."
  exit 1
fi

# exit trap: cleanup
function finish {
  echo "Deleting function '$function_name'..."
  yes | gcloud beta functions delete "$function_name" 2>"$OUT"
  echo 'Cleanup complete.'
}



###############################################################################
# test run
###############################################################################

echo 'Begin test run:'

# deploy Cloud Function
echo 'Deploying Cloud Function...'
cd "${function_path}"
function_url=$(gcloud beta functions deploy "$function_name" \
  --entry-point "$function_js" --trigger-http --project "$project_id" \
  --stage-bucket "gs://${project_id}.appspot.com" | grep "url:")
function_url=${function_url#*: }
cd - >/dev/null

trap finish EXIT

echo $function_url
echo $deployment_name

# test create, update, read, and delete
echo 'Creating the Scheduled Deployment...'
curl "${function_url}?name=${deployment_name}" -X POST \
  -H 'Content-Type:application/json' -d "@${deployment_file}"
echo ''

echo 'Retrieving the Scheduled Deployment...'
# wait for Datastore insert to propagate
sleep 120
curl "${function_url}/${deployment_name}" -X GET
echo ''

echo 'Updating a Scheduled Deployment...'
curl "${function_url}/${deployment_name}" -X PUT \
  -H 'Content-Type:application/json' -d "@${deployment_file}"
echo ''

echo 'Deleting a Scheduled Deployment.'
# wait for Datastore insert to propagate
sleep 120
curl "${function_url}/${deployment_name}" -X DELETE

echo 'Finished test run.'

