#!/usr/bin/env bats

source tests/helpers.bash

export TEST_SERVICE_ACCOUNT="test-sa-${RAND}"

# Create and save a random 10 char string in a file
RANDOM_FILE="/tmp/${FAAS_ORGANIZATION_ID}-iammember.txt"
if [[ ! -e "${RANDOM_FILE}" ]]; then
    RAND=$(head /dev/urandom | LC_ALL=C tr -dc a-z0-9 | head -c 10)
    echo ${RAND} > "${RANDOM_FILE}"
fi

# Set variables based on random string saved in the file
# envsubst requires all variables used in the example/config to be exported
if [[ -e "${RANDOM_FILE}" ]]; then
    export RAND=$(cat "${RANDOM_FILE}")
    DEPLOYMENT_NAME="${FAAS_PROJECT_ID}-iammember-${RAND}"
    CONFIG=".${DEPLOYMENT_NAME}.yaml"
fi

########## HELPER FUNCTIONS ##########

function create_config() {
    echo "Creating ${CONFIG}"
    envsubst < tests/fixtures/configs/iam-member.yaml > "${CONFIG}"
}

function delete_config() {
    echo "Deleting ${CONFIG}"
    rm -f "${CONFIG}"
}

function setup() {
    # Global setup - this gets executed only once per test file
    if [ ${BATS_TEST_NUMBER} -eq 1 ]; then
        create_config
        gcloud iam service-accounts create "${TEST_SERVICE_ACCOUNT}" \
            --project "${FAAS_PROJECT_ID}"
    fi

    # Per-test setup steps here
}

function teardown() {
    # Global teardown - this gets executed only once per test file
    if [[ "$BATS_TEST_NUMBER" -eq "${#BATS_TEST_NAMES[@]}" ]]; then
        gcloud iam service-accounts delete "${TEST_SERVICE_ACCOUNT}@${FAAS_PROJECT_ID}.iam.gserviceaccount.com" \
            --project "${FAAS_PROJECT_ID}"
        delete_config
        rm -f "${RANDOM_FILE}"
    fi

    # Per-test teardown steps here
}


@test "Creating deployment ${DEPLOYMENT_NAME} from ${CONFIG}" {
    gcloud deployment-manager deployments create "${DEPLOYMENT_NAME}" \
        --config "${CONFIG}" \
        --project "${FAAS_PROJECT_ID}"
}

@test "Verifying roles were added in deployment ${DEPLOYMENT_NAME}" {
    run gcloud projects get-iam-policy "${FAAS_PROJECT_ID}" \
        --flatten="bindings[].members" \
        --format='table(bindings.role)' \
        --filter="bindings.members:${TEST_SERVICE_ACCOUNT}@${FAAS_PROJECT_ID}.iam.gserviceaccount.com"
    [[ "$output" =~ "roles/editor" ]]
    [[ "$output" =~ "roles/viewer" ]]
}

@test "Deployment Delete" {
    gcloud deployment-manager deployments delete "${DEPLOYMENT_NAME}" -q --project "${FAAS_PROJECT_ID}"

    run gcloud projects get-iam-policy "${FAAS_PROJECT_ID}" \
        --flatten="bindings[].members" \
        --format='table(bindings.role)' \
        --filter="bindings.members:${TEST_SERVICE_ACCOUNT}@${FAAS_PROJECT_ID}.iam.gserviceaccount.com"
    [[ ! "$output" =~ "roles/editor" ]]
    [[ ! "$output" =~ "roles/viewer" ]]
}
