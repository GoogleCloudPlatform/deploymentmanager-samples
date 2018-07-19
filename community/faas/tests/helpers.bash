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
if [ ! -e ${FAAS_CONF} ]
then
    echo "Please setup your faas config file. Default ~/.faas-tests.conf. For example:"
    echo "====================="
    cat tests/faas-tests.conf.example
    echo "====================="
    exit 1
fi
source ${FAAS_CONF}

#### TEST VARIABLES ####


#### HELPER FUNCTIONS ####
