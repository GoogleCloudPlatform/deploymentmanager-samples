# Testing

This project's consistency and quality control are backed by simple integration
tests using the [Bats testing framework](https://github.com/sstephenson/bats).


## Requirements

To install bats, follow the instructions in the Bats website above (making sure
the `bats` executable is in your PATH.

Alternativelly, setup a *development environment* as described
[here](development.md):


## Setting up the testing environment

### Using a Cloud Foundation config file
Since most companies and persons using or developing against this project will
be working under a different GCP Organization, some of the base settings needed
for these tests to run were abstracted, and moved to a *personalized*
configuration file, which by default is expected to be `~/.cloud-foundation-tests.conf`,
though the location of this tests config file can be customized by setting the
variable `CLOUD_FOUNDATION_CONF`. For example:

```
export CLOUD_FOUNDATION_CONF=/etc/cloud-foundation-tests.conf
```

This file needs to be set with the site-specific information for each person or
organization. An example for this file is under
`tests/cloud-foundation-tests.conf.example`.


### Using environment variables

An alternative to using the Cloud Foundation config file is to use environment variables.
Make sure to export all variables described in the
`tests/cloud-foundation-tests.conf.example` making the necessary adjustment for your own
organization.


## Running tests

Currently, only specific test files can be executed at a time. Work is being
done to implement a full suite test runner that will execute all (or a subset)
of the tests available.

Paths are important. Always run the test from the root of the `cloud-foundation` project:

```
./tests/integration/network.bats
 ✓ Creating deployment my-gcp-project-network from my-gcp-project-network.yaml
 ✓ Verifying resources were created in deployment my-gcp-project-network
 ✓ Verifying subnets were created in deployment my-gcp-project-network
 ✓ Deployment Delete
 ✓ Verifying resources were deleted in deployment my-gcp-project-network
 ✓ Verifying subnets were deleted in deployment my-gcp-project-network
```

It's important to notice that the test files attempt to remain similar much as possible
to the *example configs* available under each of the respective template `examples/` directory.
This will keep examples consistent with the tests.


## Temporary files and fixtures

When running tests, temporary Deployment Manager configs, and fixtures
are often created, and deleted via *teardown()* function.

Due to the fact that a DM config file needs to be located relative to the
templates it uses, these configs are usually created in the root of the
project, for example, in the network template mentioned, the config
`.${CLOUD_FOUNDATION_PROJECT_ID}-network.yaml` will be temporarily created (and deleted
at the end of the execution).

Other temporary files are created under `/tmp`, for example:
```
/tmp/${CLOUD_FOUNDATION_ORGANIZATION_ID}-network.txt
/tmp/${CLOUD_FOUNDATION_ORGANIZATION_ID}-project.txt
```

These names could change later. But if weirdness is observed during test
execution, these are good places to start looking for hints about what the
problem might be.
