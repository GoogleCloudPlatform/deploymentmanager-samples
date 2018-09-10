#!/usr/bin/env bats

source tests/helpers.bash

TEST_NAME=$(basename "${BATS_TEST_FILENAME}" | cut -d '.' -f 1)

## Create and save a random 10 char string in a file
RANDOM_FILE="/tmp/${CLOUD_FOUNDATION_ORGANIZATION_ID}-${TEST_NAME}.txt"
if [[ ! -e "${RANDOM_FILE}" ]]; then
    RAND=$(head /dev/urandom | LC_ALL=C tr -dc a-z0-9 | head -c 10)
    echo ${RAND} > "${RANDOM_FILE}"
fi

# Set variables based on random string saved in the file
# envsubst requires all variables used in the example/config to be exported
if [[ -e "${RANDOM_FILE}" ]]; then
    export RAND=$(cat "${RANDOM_FILE}")
    DEPLOYMENT_NAME="${CLOUD_FOUNDATION_PROJECT_ID}-${TEST_NAME}-${RAND}"
    # Deployment names cannot have underscores. Replace with dashes.
    DEPLOYMENT_NAME=${DEPLOYMENT_NAME//_/-}
    CONFIG=".${DEPLOYMENT_NAME}.yaml"
fi

export PROJECT_NUMBER=$(gcloud projects list | grep dev-island | awk '{ print $3}')

########## HELPER FUNCTIONS ##########

function create_config() {
    echo "Creating ${CONFIG}"
    envsubst < "templates/cloud_spanner/tests/integration/${TEST_NAME}.yaml" > "${CONFIG}"
}

function delete_config() {
    echo "Deleting ${CONFIG}"
    rm -f "${CONFIG}"
}

function setup() {
    if [ ${BATS_TEST_NUMBER} -eq 1 ]; then
        create_config
    fi
}

function teardown() {
    if [[ "$BATS_TEST_NUMBER" -eq "${#BATS_TEST_NAMES[@]}" ]]; then
        rm -f "${RANDOM_FILE}"
        delete_config
    fi
}

@test "Creating deployment ${DEPLOYMENT_NAME} from ${CONFIG}" {
    gcloud deployment-manager deployments create "${DEPLOYMENT_NAME}" \
        --config ${CONFIG} \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}"
}

@test "Verifying spanner cluster is created as part of ${DEPLOYMENT_NAME}" {
    run gcloud spanner instances list myspannercluster-"${RAND}" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ "$output" =~ "myspannercluster-${RAND}" ]]
}

@test "Verifying spanner cluster IAM is created as part of ${DEPLOYMENT_NAME}" {
    run gcloud spanner instances get-iam-policy myspannercluster-"${RAND}" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ "$output" =~ "${PROJECT_NUMBER}@cloudservices.gserviceaccount.com" ]]
}

@test "Verifying spanner DB is created as part of ${DEPLOYMENT_NAME}" {
    run gcloud spanner databases list --instance myspannercluster-"${RAND}" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ "$output" =~ "spannerdb1" ]]
}

@test "Verifying spanner DB IAM is created as part of ${DEPLOYMENT_NAME}" {
    run gcloud spanner databases get-iam-policy spannerdb1 --instance myspannercluster-"${RAND}" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ "$output" =~ "role: roles/spanner.databaseAdmin" ]]
}

@test "Deployment Delete" {
    gcloud deployment-manager deployments delete "${DEPLOYMENT_NAME}" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}" -q
    run gcloud  run gcloud spanner instances list \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ ! "$output" =~ "myspannercluster-${RAND}" ]]
}
