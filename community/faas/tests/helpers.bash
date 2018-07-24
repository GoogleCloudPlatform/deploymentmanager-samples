#!/bin/bash

# This file is meant to hold common variables and functions to be used by the
# testing suite (bats).
#
# Tests need to run against the user's own organization/projects/etc, so the
# most basic configs are read and exported from the user's own
# `~/.faas-test.conf`.
#
# An example for this config is placed under `tests/faas-tests.conf`. Users should
# move this file to `~/.faas-test.conf` and tweak according to their own GCP
# organizational structure

FAAS_CONF=${FAAS_CONF-~/.faas-tests.conf}

if [[ -z "${FAAS_ORGANIZATION_ID}" || -z "${FAAS_BILLING_ACCOUNT_ID}" || -z "${FAAS_PROJECT_ID}" ]]; then
    if [[ ! -e ${FAAS_CONF} ]]; then
        echo "Please setup your environment variables or faas config file"
        echo "Default location for config: ~/.faas-tests.conf. Example:"
        echo "====================="
        cat tests/faas-tests.conf.example
        echo "====================="
        exit 1
    fi
    source ${FAAS_CONF}
fi
