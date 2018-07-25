#!/usr/bin/env bats

source tests/helpers.bash

# Create and save a random 10 char string in a file
RANDOM_FILE="/tmp/${FAAS_ORGANIZATION_ID}-cloudrouter.txt"
if [[ ! -e "${RANDOM_FILE}" ]]; then
    RAND=$(head /dev/urandom | LC_ALL=C tr -dc a-z0-9 | head -c 10)
    echo ${RAND} > "${RANDOM_FILE}"
fi

# Set variables based on random string saved in the file
# envsubst requires all variables used in the example/config to be exported
if [[ -e "${RANDOM_FILE}" ]]; then
    export RAND=$(cat "${RANDOM_FILE}")
    DEPLOYMENT_NAME="${FAAS_PROJECT_ID}-cloudrouter"
    CONFIG=".${DEPLOYMENT_NAME}.yaml"
fi

########## HELPER FUNCTIONS ##########

function create_config() {
    echo "Creating ${CONFIG}"
    envsubst < tests/fixtures/configs/cloud_router.yaml > "${CONFIG}"
}

function delete_config() {
    echo "Deleting ${CONFIG}"
    rm -f "${CONFIG}"
}

function setup() {
    # Global setup - this gets executed only once per test file
    if [ ${BATS_TEST_NUMBER} -eq 1 ]; then
        gcloud compute networks create network-${RAND} \
            --project "${FAAS_PROJECT_ID}" \
            --description "integration test ${RAND}" \
            --subnet-mode custom
        create_config
    fi

  # Per-test setup steps here
  }

function teardown() {
    # Global teardown - this gets executed only once per test file
    if [[ "$BATS_TEST_NUMBER" -eq "${#BATS_TEST_NAMES[@]}" ]]; then
        gcloud compute networks delete network-${RAND} --project "${FAAS_PROJECT_ID}" -q
        rm -f "${RANDOM_FILE}"
        delete_config
    fi

    # Per-test teardown steps
}


@test "Creating deployment ${DEPLOYMENT_NAME} from ${CONFIG}" {
  gcloud deployment-manager deployments create "${DEPLOYMENT_NAME}" --config ${CONFIG} --project "${FAAS_PROJECT_ID}"
}

@test "Verifying routers were created in deployment ${DEPLOYMENT_NAME}" {
  run gcloud compute routers list --project "${FAAS_PROJECT_ID}"
  [[ "$output" =~ "cloud-router-${RAND}" ]]
}

@test "Deployment Delete" {
  gcloud deployment-manager deployments delete "${DEPLOYMENT_NAME}" --project "${FAAS_PROJECT_ID}" -q

  run gcloud compute routers list --project "${FAAS_PROJECT_ID}"
  [[ ! "$output" =~ "cloud-router-${RAND}" ]]
}
