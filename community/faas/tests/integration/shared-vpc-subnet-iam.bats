#!/usr/bin/env bats

source tests/helpers.bash

export TEST_SERVICE_ACCOUNT="test-sa-${RAND}"


# Create and save a random 10 char string in a file
RANDOM_FILE="/tmp/${FAAS_ORGANIZATION_ID}-shared-vpc-subnet-iam.txt"
if [[ ! -e "${RANDOM_FILE}" ]]; then
    RAND=$(head /dev/urandom | LC_ALL=C tr -dc a-z0-9 | head -c 10)
    echo ${RAND} > "${RANDOM_FILE}"
fi

# Set variables based on random string saved in the file
# envsubst requires all variables used in the example/config to be exported
if [[ -e "${RANDOM_FILE}" ]]; then
    export RAND=$(cat "${RANDOM_FILE}")
    DEPLOYMENT_NAME="${FAAS_PROJECT_ID}-shared-vpc-subnet-iam-${RAND}"
    CONFIG=".${DEPLOYMENT_NAME}.yaml"
fi

########## HELPER FUNCTIONS ##########

function create_config() {
    echo "Creating ${CONFIG}"
    envsubst < tests/fixtures/configs/shared-vpc-subnet-iam.yaml > "${CONFIG}"
}

function delete_config() {
    echo "Deleting ${CONFIG}"
    rm -f "${CONFIG}"
}

function setup() {
    # Global setup - this gets executed only once per test file
    if [ ${BATS_TEST_NUMBER} -eq 1 ]; then
        gcloud compute networks create "network-${RAND}" \
            --project "${FAAS_PROJECT_ID}" \
            --description "integration test ${RAND}" \
            --subnet-mode custom
        gcloud compute networks subnets create "subnet-${RAND}-1" \
            --project "${FAAS_PROJECT_ID}" \
            --network "network-${RAND}" \
            --range 10.118.8.0/22 \
            --region us-east1
        gcloud compute networks subnets create "subnet-${RAND}-2" \
            --project "${FAAS_PROJECT_ID}" \
            --network "network-${RAND}" \
            --range 192.168.0.0/16 \
            --region us-east1
        gcloud iam service-accounts create "${TEST_SERVICE_ACCOUNT}" \
            --project "${FAAS_PROJECT_ID}"
        create_config
    fi

    # Per-test setup steps here
}

function teardown() {
    # Global teardown - this gets executed only once per test file
    if [[ "$BATS_TEST_NUMBER" -eq "${#BATS_TEST_NAMES[@]}" ]]; then
        gcloud compute networks subnets delete "subnet-${RAND}-2" --region us-east1 \
            --project "${FAAS_PROJECT_ID}" -q
        gcloud compute networks subnets delete "subnet-${RAND}-1" --region us-east1 \
            --project "${FAAS_PROJECT_ID}" -q
        gcloud compute networks delete network-${RAND} --project "${FAAS_PROJECT_ID}" -q
        gcloud iam service-accounts delete "${TEST_SERVICE_ACCOUNT}@${FAAS_PROJECT_ID}.iam.gserviceaccount.com" \
            --project "${FAAS_PROJECT_ID}" -q
        delete_config
        rm -f "${RANDOM_FILE}"
    fi

    # Per-test teardown steps here
}


@test "Creating deployment ${DEPLOYMENT_NAME} from ${CONFIG}" {
    gcloud deployment-manager deployments create "${DEPLOYMENT_NAME}" --config "${CONFIG}" \
        --project "${FAAS_PROJECT_ID}"
}

@test "Verifying roles were created in deployment ${DEPLOYMENT_NAME}" {
    run gcloud beta compute networks subnets get-iam-policy "subnet-${RAND}-1" --region us-east1 \
        --project "${FAAS_PROJECT_ID}" --filter="bindings.members:${TEST_SERVICE_ACCOUNT}"
    [[ "$output" =~ "serviceAccount:${TEST_SERVICE_ACCOUNT}@${FAAS_PROJECT_ID}.iam.gserviceaccount.com" ]]
    [[ "$output" =~ "roles/compute.networkUser" ]]

    run gcloud beta compute networks subnets get-iam-policy "subnet-${RAND}-2" --region us-east1 \
        --project "${FAAS_PROJECT_ID}" --filter="bindings.members:${TEST_SERVICE_ACCOUNT}"
    [[ "$output" =~ "serviceAccount:${TEST_SERVICE_ACCOUNT}@${FAAS_PROJECT_ID}.iam.gserviceaccount.com" ]]
    [[ "$output" =~ "roles/compute.networkUser" ]]
}

@test "Deployment Delete" {
    gcloud deployment-manager deployments delete "${DEPLOYMENT_NAME}" -q --project "${FAAS_PROJECT_ID}"
}
