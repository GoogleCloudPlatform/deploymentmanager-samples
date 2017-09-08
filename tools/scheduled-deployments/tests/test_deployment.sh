#!/bin/bash
#
# Integration test script for Scheduled Deployments.
#
# Test script creates a Cloud Function triggered by a Pub/Sub topic. The
# function accesses Datastore and invokes Deployment Manager to deploy all
# listed configurations.

set -e -u

source gbash.sh || exit


###############################################################################
# setup
###############################################################################

DEFINE_string prefix 'sd-' 'Prefix to append to name of deployment resources.'
DEFINE_string --required project '' 'Project ID to use in test.'
DEFINE_string trigger_topic 'timer' 'Name of Pub/Sub topic.'
DEFINE_string function_path '../functions' \
  'Path to directory containing index.js functions.'
DEFINE_string function_js 'deployScheduledDeployments' \
  'Name of Javascript function to be triggered by Cloud Function.'
DEFINE_string function_name 'deploy-function' \
  'Name of Pub/Sub-triggered Cloud Function.'
DEFINE_bool debug --empty_false 'false' \
  'Turn debug mode on, outputting all output from commands.'

gbash::init_google "$@"

prefix="$FLAGS_prefix"
project_id="$FLAGS_project"
project_stage_bucket="${project_id}.appspot.com"
trigger_topic="${prefix}${FLAGS_trigger_topic}"
function_path="$FLAGS_function_path"
function_js="$FLAGS_function_js"
function_name="${prefix}${FLAGS_function_name}"

# set debug mode on or off
if [ $FLAGS_debug ]; then
  OUT='/dev/tty'
else
  OUT='/dev/null'
fi

# ensure project ID is valid
if ! gcloud projects describe "$project_id" >/dev/null 2>&1; then
  echo "ERROR: Project ID '$project_id' does not exist, or you do not have " \
    "permission to access it."
  exit 1
fi

# ensure function name is not already used
if gcloud beta functions describe "$function_name" --project "$project_id" \
  >/dev/null 2>&1; then
  echo "ERROR: A function with the name '$function_name' already exists."
  exit 1
fi

# ensure index.js exists in function path
if [[ ! -e "${function_path}/index.js" ]]; then
  echo "ERROR: File 'index.js' does not exist in path '$function_path'."
  exit 1
fi


# exit trap: cleanup
function finish {
  echo "Deleting Cloud Function '$function_name'..."
#  yes | gcloud beta functions delete "$function_name" --project "$project_id" \
    2>"$OUT"
  echo "Deleting Pub/Sub topic '$trigger_topic'..."
#  gcloud beta pubsub topics delete "$trigger_topic" --project "$project_id" \
    2>"$OUT"

  # delete all newly-made deployments
  echo 'Deleting deployments...'
  deployments_to_delete=$(gcloud deployment-manager deployments list \
    --simple-list --project "$project_id" | grep "^${prefix}")
  for deployment in $(echo "$deployments_to_delete"); do
    yes | gcloud deployment-manager deployments delete "$deployment" \
      --project "$project_id" 2>"$OUT"
    echo "  Deleted deployment '$deployment'."
  done
  echo 'Cleanup complete.'
}


###############################################################################
# test run
###############################################################################

echo 'Begin test run:'
trap finish EXIT

# create Pub/Sub topic
echo 'Creating Pub/Sub topic...'
gcloud beta pubsub topics create "$trigger_topic" --project "$project_id" \
  2>"$OUT"

# deploy Cloud Function
echo 'Deploying Cloud Function...'
cd "$function_path"
gcloud beta functions deploy "$function_name" --entry-point "$function_js" \
  --stage-bucket "$project_stage_bucket" --trigger-topic "$trigger_topic" \
  --project "$project_id" >"$OUT" 2>&1
cd - >/dev/null

# trigger Pub/Sub topic
echo 'Triggering Pub/Sub topic...'
#sleep 60  # Cloud Function needs to get settled in
gcloud beta pubsub topics publish "$trigger_topic" "testing" \
  --project "$project_id" >"$OUT"

# confirm deployment was made
sleep 60  # allow changes to propagate
echo 'The following deployments have been made:'
gcloud deployment-manager deployments list --project "$project_id" \
  | grep "^${prefix}"

echo 'Finished test run.'

