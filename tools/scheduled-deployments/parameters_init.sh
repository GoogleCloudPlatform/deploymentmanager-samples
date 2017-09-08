#!/bin/bash
#
# Script to initialize values in the Open API Specification file for the
# Scheduled Deployments type provider and the configuration file.

set -e -u

source gbash.sh || exit

DEFINE_string project --required '' 'Cloud project ID.'
DEFINE_string spec --required 'openapi.yaml' \
  'Path to OpenAPI Specification file.'
DEFINE_string config --required 'sd_config.yaml' \

DEFINE_string region --required 'us-central1' \
  'The region where function is deployed.'
DEFINE_string function_name --required 'sd-router' 'Name of Cloud Function.'
DEFINE_string type_provider --required 'sd-type-provider' \
  'Name of type provider.'
DEFINE_string user --required 'test-user' 'Name of user.'

gbash::init_google "$@"


sed -i "s|\[REGION\]|${FLAGS_region}|g" "$FLAGS_spec"
sed -i "s|\[PROJECT-ID\]|${FLAGS_project}|g" "$FLAGS_spec"
sed -i "s|\[ROUTER-FUNCTION-NAME\]|${FLAGS_function_name}|g" "$FLAGS_spec"


sed -i "s|\[ROUTER-FUNCTION-NAME\]|${FLAGS_function_name}|g" "$FLAGS_config"
sed -i "s|\[PROJECT-ID\]|${FLAGS_project}|g" "$FLAGS_config"
sed -i "s|\[TYPE-PROVIDER-NAME\]|${FLAGS_type_provider}|g" "$FLAGS_config"
sed -i "s|\[USER\]|${FLAGS_user}|g" "$FLAGS_config"

