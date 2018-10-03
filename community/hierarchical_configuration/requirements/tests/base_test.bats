#!/usr/bin/env bats

#source tests/helpers.bash

TEST_NAME=$(basename "${BATS_TEST_FILENAME}" | cut -d '.' -f 1)

# Create and save a random 10 char string in a file
#RANDOM_FILE="/tmp/${CLOUD_FOUNDATION_ORGANIZATION_ID}-${TEST_NAME}.txt"
#if [[ ! -e "${RANDOM_FILE}" ]]; then
#    RAND=$(head /dev/urandom | LC_ALL=C tr -dc a-z0-9 | head -c 10)
#    echo ${RAND} > "${RANDOM_FILE}"
#fi

# Set variables based on random string saved in the file
# envsubst requires all variables used in the example/config to be exported
#if [[ -e "${RANDOM_FILE}" ]]; then
#    export RAND=$(cat "${RANDOM_FILE}")
#    DEPLOYMENT_NAME="${CLOUD_FOUNDATION_PROJECT_ID}-${TEST_NAME}-${RAND}"
#    # Deployment names cannot have underscores. Replace with dashes.
#    DEPLOYMENT_NAME=${DEPLOYMENT_NAME//_/-}
#    CONFIG=".${DEPLOYMENT_NAME}.yaml"
#fi

########## HELPER FUNCTIONS ##########

#function create_config() {
#    echo "Creating ${CONFIG}"
#    envsubst < "templates/firewall/tests/integration/${TEST_NAME}.yaml" > "${CONFIG}"
#}

#function delete_config() {
#    echo "Deleting ${CONFIG}"
#    rm -f "${CONFIG}"
#}

function setup() {
#    # Global setup - this gets executed only once per test file
#    if [ ${BATS_TEST_NUMBER} -eq 1 ]; then
#        create_config
#        gcloud compute networks create network-test-${RAND} \
#            --project "${CLOUD_FOUNDATION_PROJECT_ID}" \
#            --description "integration test ${RAND}" \
#            --subnet-mode custom
#    fi
#
#    # Per-test setup steps here

	gcloud config set deployment_manager/glob_imports True
}

#function teardown() {
#    # Global teardown - this gets executed only once per test file
#    if [[ "$BATS_TEST_NUMBER" -eq "${#BATS_TEST_NAMES[@]}" ]]; then
#        delete_config
#        gcloud compute networks delete network-test-${RAND} \
#            --project "${CLOUD_FOUNDATION_PROJECT_ID}" -q
#        rm -f "${RANDOM_FILE}"
# #   fi
#
#    # Per-test teardown steps here
#}


@test "Creating deployment hierarchy-basic-dev from Basic/env_demo_project.py" {
    gcloud deployment-manager deployments create hierarchy-basic-dev --template Basic/env_demo_project.py --properties=envName:dev
}

@test "Creating deployment hierarchy-org-ecom-dev from Organization_with_departments/systems/my_ecom_system/env_demo_project.py" {
    gcloud deployment-manager deployments create hierarchy-org-ecom-dev --template Organization_with_departments/systems/my_ecom_system/env_demo_project.py --properties=envName:dev
}

@test "Creating deployment hierarchy-org-proj-dev from Organization_with_departments/systems/System_with_project_creation/project_creation.py" {
    gcloud deployment-manager deployments create hierarchy-org-proj-dev --template Organization_with_departments/systems/System_with_project_creation/project_creation.py --properties=envName:dev
}

@test "Creating deployment hierarchy-org-helper-dev from Organization_with_departments/systems/System_with_project_creation_and_helper_function/project_creation.py" {
    gcloud deployment-manager deployments create hierarchy-org-helper-dev --template Organization_with_departments/systems/System_with_project_creation_and_helper_function/project_creation.py --properties=envName:dev
}

#@test "Verifying resources were created in deployment ${DEPLOYMENT_NAME}" {
#    run gcloud compute firewall-rules list --project "${CLOUD_FOUNDATION_PROJECT_ID}"
#    [[ "$output" =~ "allow-proxy-from-inside" ]]
#    [[ "$output" =~ "allow-dns-from-inside" ]]
#}

@test "Deployment Delete" {
    gcloud deployment-manager deployments delete hierarchy-basic-dev -q
    gcloud deployment-manager deployments delete hierarchy-org-ecom-dev -q
    gcloud deployment-manager deployments delete hierarchy-org-proj-dev -q
    gcloud deployment-manager deployments delete hierarchy-org-helper-dev -q

   # run gcloud compute firewall-rules list --project "${CLOUD_FOUNDATION_PROJECT_ID}"
   # [[ ! "$output" =~ "allow-proxy-from-inside" ]]
   # [[ ! "$output" =~ "allow-dns-from-inside" ]]
}