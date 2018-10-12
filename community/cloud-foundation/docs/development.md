# Development

The Cloud Foundation Toolkit project is comprised of two parts:

* An extensive, production-quality DM template library.
* A command line Python utility (cft) that can manage multiple DM deployments
  and dependencies between them.

These two pieces can be developed fairly independently, and it is possible that
sometime in the future they become two independent projects.

Since both development lifecycle and tooling used to develop the templates and
the tool are quite decoupled from each other, two sets of development
instructions are available: One for the templates, and one for the tool.

Both sets of instructions make use of a single `Makefile`.


## Common Prerequisites

### Google Cloud SDK

The main prerequisite for both the templates and the `cft` tool is the
[Google Cloud SDK](https://cloud.google.com/sdk/), which includes the `gcloud`
command line utility.

Unfortunately, since the SDK is not in *pypi*, its installation can't be easily
automated from within this project, due to users in different platforms needing
different packages. Just follow the installation instruction for the SDK found
in the official link above.

**IMPORTANT**: the `cft` utility requires the `gcloud` command to be in the
users' PATH. This is normally done automatically if installing the SDK via the
official package manager for the user's OS (RPM, DEB, etc); or even if using
the installer (`install.sh`) bundled in the linux tarball. If not using any
installation methods described in the page, users need to ensure `gcloud` can
be found in one of the directory of the PATH environment variable, because
it's via `gcloud` that `cft` can find the location of the python libraries
included in the SDK.


# CFT Utility Development

The development environment for the `cft` utility is based on
[tox](https://tox.readthedocs.io/en/latest/index.html) for streamlining the
management of Python virtual environments, and
[pytest](https://docs.pytest.org/en/latest/contents.html) for unit tests.

## CFT Utility Prerequisites

Since Tox creates virtual environments, this package often must be installed
with the system python, unless the user has a more complex setup, in which case
the user should be able to figure out the idisyncrasies of his/her setup:

```
sudo make cft-prequisites
```

## Creating the CFT Development Environment

The supported way of development is via the virtual environment created by
`tox`.
The block of code below creates a virtual environment called `venv`
with `tox` in the root of the project directory:

```
make cft-venv
```

Now activate the virtual environment, which unfortunately cannot easily be
added to the `Makefile` since `make` creates sanitized sub-shells for each
command, and the parent shell doesn't get the environment variables that the
virtual environment sets up on activation:

```
# activates VE, then finds Google SDK path, and adds libraries to PYTHONPATH
source venv/bin/activate
source src/cftenv
```

It's worth mentioning that `tox.ini` in this project is configured to
"*install*" the utility using Pip's "develop" mode, ie, the pip **doesn't**
actually packages and installs the utility in the virtual environment's
`site-packages`.

Also worth mentioning that if any packages need to be installed or updated in
any existing virtual environment created by `tox`, the virtual environment must
be deleted and recreated:

## Deleting the Utility Development Environment

First *deactivate* the virtual environment (if activated)

```
deactivate
unset CLOUDSDK_ROOT_DIR CLOUDSDK_PYTHON_SITEPACKAGES PYTHONPATH
```

Delete the development vitual environment

```
make cft-clean-venv
```


## Unit Tests

Unit tests for the utility can be fired up in different ways depending how and
what the user wants to test:

### Running All Tests From Outside The Development Environment

This is normally done if running the tests from a CI tool. For this, `tox`
creates the necessary virtual environments (not `venv`, which is used only for
active development), and run all the tests within those VEs:

```
make cft-test
```

### Running All Tests From Within The Development Environment

This is normally done when one is actively developing within the develpment
virtual environment, meaning the `venv` must be activated`, and `src/cftdev`
sourced in order to get PYTHONPATH set as mentioned above.

```
# using the make target to run all tests
make cft-test-venv

# alternatively, using pytest directly to run all tests
python -m pytest -v

# or run a single test file
python -m pytest -v tests/unit/test_deployment.py
```


# Template Development

For template development, these tools are needed:
* [Google Cloud SDK](https://cloud.google.com/sdk/)
* [bats](https://github.com/sstephenson/bats) for testing

The instructions to setup the SDK are in the official website above.

In order to keep things tidy, and avoid the need for root/sudo, it's
recommended to install `bats` inside the `venv` development environment as
decribed above. For that run:

```
make template-prerequisites
```

Installing `bats` system-wide should also work, as long as it's the PATH.
