#!/usr/bin/env bats

source tests/helpers.bash

TEST_NAME=$(basename "${BATS_TEST_FILENAME}" | cut -d '.' -f 1)

# Create a random 10-char string and save it in a file.
RANDOM_FILE="/tmp/${CLOUD_FOUNDATION_ORGANIZATION_ID}-${TEST_NAME}.txt"
if [[ ! -e "${RANDOM_FILE}" ]]; then
    RAND=$(head /dev/urandom | LC_ALL=C tr -dc a-z0-9 | head -c 10)
    echo ${RAND} > "${RANDOM_FILE}"
fi

# Set variables based on the random string saved in the file.
# envsubst requires all variables used in the example/config to be exported.
if [[ -e "${RANDOM_FILE}" ]]; then
    export RAND=$(cat "${RANDOM_FILE}")
    DEPLOYMENT_NAME="${CLOUD_FOUNDATION_PROJECT_ID}-${TEST_NAME}-${RAND}"
    # Replace underscores in the deployment name with dashes.
    DEPLOYMENT_NAME=${DEPLOYMENT_NAME//_/-}
    CONFIG=".${DEPLOYMENT_NAME}.yaml"
    CONFIG_FLEX=".${DEPLOYMENT_NAME}-flex.yaml"
fi

########## HELPER FUNCTIONS ##########

function create_config() {
    echo "Creating ${CONFIG}"
    envsubst < ${BATS_TEST_DIRNAME}/${TEST_NAME}.yaml > "${CONFIG}"
    envsubst < ${BATS_TEST_DIRNAME}/${TEST_NAME}_flex.yaml > "${CONFIG_FLEX}"
}

function delete_config() {
    echo "Deleting ${CONFIG}"
    rm -f "${CONFIG}"
    rm -f "${CONFIG_FLEX}"
}

function setup() {
    # Global setup; executed once per test file.
    if [ ${BATS_TEST_NUMBER} -eq 1 ]; then
        create_config
        # Create a public bucket
        gsutil mb -l us-east1 gs://test-bucket-${RAND}
        # Copy the sample code to the bucket
        gsutil cp -r ${BATS_TEST_DIRNAME}/src gs://test-bucket-${RAND}
        # Give the bucket public permissions
        gsutil acl -r ch -u AllUsers:R gs://test-bucket-${RAND}/src/
    fi

    # Per-test setup steps.
}

function teardown() {
    # Global teardown; executed once per test file.
    if [[ "$BATS_TEST_NUMBER" -eq "${#BATS_TEST_NAMES[@]}" ]]; then
        gsutil rm -r gs://test-bucket-${RAND}/*
        gsutil rb gs://test-bucket-${RAND}
        delete_config
        rm -f "${RANDOM_FILE}"
    fi

    # Per-test teardown steps.
}

@test "Creating deployment ${DEPLOYMENT_NAME} from ${CONFIG}" {
    run gcloud deployment-manager deployments create "${DEPLOYMENT_NAME}" \
        --config "${CONFIG}" --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ "$status" -eq 0 ]]

    # Create two seperate deployments. For a new app, the first service
    # must be deployed under a serviceId of "default" which will be the
    # app engine standard deployment. The second can be under a different
    # service Id. If both were deployed under the "default" services Id,
    # the deployment will fail with an "already processing" error since
    # there would be two apps being deployed for the first time under the
    # same service name
    run gcloud deployment-manager deployments create "${DEPLOYMENT_NAME}-flex" \
        --config "${CONFIG_FLEX}" --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ "$status" -eq 0 ]]
}

@test "Verifying app resource was created in deployment ${DEPLOYMENT_NAME}" {
    run gcloud app describe --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ "$status" -eq 0 ]]
    [[ "$output" =~ "id: ${CLOUD_FOUNDATION_PROJECT_ID}" ]]
    [[ "$output" =~ "locationId: us-east1" ]]
    [[ "$output" =~ "servingStatus: SERVING" ]]
}

@test "Verifying standard app engine resource were created in deployment ${DEPLOYMENT_NAME}" {
    run gcloud app versions list --filter="version:test-ae-std-${RAND}" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ "$status" -eq 0 ]]
    [[ "$output" =~ "test-ae-std-${RAND}" ]]

    run gcloud app versions describe "test-ae-std-${RAND}" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}" \
        --service="std-${RAND}"
    [[ "$status" -eq 0 ]]
    [[ "$output" =~ "test-ae-std-${RAND}" ]]
    [[ "$output" =~ "env: standard" ]]

    run curl "https://default-dot-${CLOUD_FOUNDATION_PROJECT_ID}.appspot.com/"
    [[ "$status" -eq 0 ]]
    [[ "$output" =~ "Hello, World!" ]]
}

@test "Verifying flex app engine resource were created in deployment ${DEPLOYMENT_NAME}-flex" {
    run gcloud app versions list --filter="version:test-ae-flex-${RAND}" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ "$status" -eq 0 ]]
    [[ "$output" =~ "test-ae-flex-${RAND}" ]]

    run gcloud app instances list --filter="version:test-ae-flex-${RAND}" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ "$status" -eq 0 ]]
    [[ "$output" =~ "test-ae-flex-${RAND}" ]]

    run gcloud app versions describe "test-ae-flex-${RAND}" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}" \
        --service="flex-${RAND}"
    [[ "$status" -eq 0 ]]
    [[ "$output" =~ "test-ae-flex-${RAND}" ]]
    [[ "$output" =~ "manualScaling:" ]]
    [[ "$output" =~ "instances: 5" ]]
    [[ "$output" =~ "env: flexible" ]]

    run curl "https://flex-${RAND}-dot-${CLOUD_FOUNDATION_PROJECT_ID}.appspot.com/"
    [[ "$status" -eq 0 ]]
    [[ "$output" =~ "Hello World!" ]]
}

########### NOTE ##################
# GAE Applications cannot be deleted once they had been created.
# Refer to README.md for additional information.
##################################
