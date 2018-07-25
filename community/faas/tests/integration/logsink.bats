#!/usr/bin/env bats

source tests/helpers.bash

# Create and save a random 10 char string in a file
RANDOM_FILE="/tmp/${FAAS_ORGANIZATION_ID}-logsink.txt"
if [[ ! -e "${RANDOM_FILE}" ]]; then
    RAND=$(head /dev/urandom | LC_ALL=C tr -dc a-z0-9 | head -c 10)
    echo ${RAND} > "${RANDOM_FILE}"
fi

# Set variables based on random string saved in the file
# envsubst requires all variables used in the example/config to be exported
if [[ -e "${RANDOM_FILE}" ]]; then
    export RAND=$(cat "${RANDOM_FILE}")
    DEPLOYMENT_NAME="${FAAS_PROJECT_ID}-logsink-${RAND}"
    CONFIG=".${DEPLOYMENT_NAME}.yaml"
fi

########## HELPER FUNCTIONS ##########

function create_config() {
    echo "Creating ${CONFIG}"
    envsubst < tests/fixtures/configs/logsink.yaml > "${CONFIG}"
}

function delete_config() {
    echo "Deleting ${CONFIG}"
    rm -f "${CONFIG}"
}

function setup() {
    # Global setup - this gets executed only once per test file
    if [ ${BATS_TEST_NUMBER} -eq 1 ]; then
        create_config
        gcloud pubsub topics create test-topic-${RAND}
        gsutil mb -l us-east1 gs://test-bucket-${RAND}/
        bq mk test_dataset_${RAND}
    fi

  # Per-test setup as per documentation
}

function teardown() {
    Global teardown - this gets executed only once per test file
    if [[ "$BATS_TEST_NUMBER" -eq "${#BATS_TEST_NAMES[@]}" ]]; then
        gsutil rm -r gs://test-bucket-${RAND}/
        gcloud pubsub topics delete test-topic-${RAND}
        bq rm -rf test_dataset_${RAND}
        delete_config
    fi

  # Per-test teardown as per documentation
}


@test "Creating deployment ${DEPLOYMENT_NAME} from ${CONFIG}" {
    gcloud deployment-manager deployments create "${DEPLOYMENT_NAME}" --config "${CONFIG}" --project "${FAAS_PROJECT_ID}"
}

@test "Verifying sinks were created each with a different as the destination in deployment ${DEPLOYMENT_NAME}" {
    run gcloud logging sinks list --project "${FAAS_PROJECT_ID}"
    [[ "$output" =~ "test-logsink-bq-${RAND}" ]]
    [[ "$output" =~ "test-logsink-pubsub-${RAND}" ]]
    [[ "$output" =~ "test-logsink-storage-${RAND}" ]]
}

@test "Deployment Delete" {
    gcloud deployment-manager deployments delete "${DEPLOYMENT_NAME}" -q --project "${FAAS_PROJECT_ID}"

    run gcloud logging sinks list --project "${FAAS_PROJECT_ID}"
    [[ ! "$output" =~ "test-logsink-bq-${RAND}" ]]
    [[ ! "$output" =~ "test-logsink-pubsub-${RAND}" ]]
    [[ ! "$output" =~ "test-logsink-storage-${RAND}" ]]
}
