#
# The correct way to setup a dev environment:
#
# $ sudo make virtualenv-requirements
# $ make virtualenv
# $ source virtualenv/bin/activate
# $ make development
#

# And the correct way of deleting the dev environment:
# 
# $ deactivate
# $ make clean-venv (or make clean-all)
#

PACKAGE := cloud_foundation
TESTDIR := tests
PYTHON  := python2.7
SHELL   := /bin/bash

help:
	@echo "virtualenv     Create a virtualenv"
	@echo "development    Install dependencies and install package in editable mode"
	@echo "style          Run style checks and coverage: "
	@echo "test           Run tests"
	@echo "clean clean-all  Clean up and clean up removing virtualenv"

.ONESHELL:
.PHONY: clean clean-all clean-virtualenv development development-requirements virtualenv
#.PHONY: check check-style check-coverage test dist develop install clean-all clean clean-venv ci-build ci-test ci-upload ci-cleanup install-test-requirements clean-pip-dependencies


virtualenv-requirements:
	${PYTHON} -m pip install --upgrade pip
	${PYTHON} -m pip install --upgrade virtualenv

development-requirements:
	${PYTHON} -m pip install --upgrade pip
	${PYTHON} -m pip install -r requirements/development.txt

#
# Configure virtual + dev environment
#

# install virtual environment
# IMPORTANT: activate venv after running this
virtualenv:
	${PYTHON} -m virtualenv $@
	@echo "===> IMPORTANT: Activate your virtual environment if you're developing locally:"
	@echo "========># source $@/bin/activate"
	@touch $@

# install package in develoment mode (for local dev only!)
development:
#	${PYTHON} -m pip install -e .
	${PYTHON} -m pip install -r requirements/development.txt
	${PYTHON} -m pip install -r requirements/install.txt
	git clone https://github.com/sstephenson/bats.git && cd bats && ./install.sh ../virtualenv




#
# style, coverage and tests
#

# checks code style
style:
	${PYTHON} -m yapf -r templates -i
#	${PYTHON} -m pylint

# tests the tool
#test: 
#	${PYTHON} -m pytest


#
# cleanup
#
clean-all: clean-virtualenv clean

# cleans up python compiled files, built packages, tests results, caches, etc
clean:
	find . \( -path '*__pycache__/*' -o -name __pycache__ \) -delete
	rm -rf build dist *.egg-info .cache .eggs .coverage

# cleans up a python virtual environment.
# IMPORTANT: deactivate virtualenv prior to running this!
clean-virtualenv:
	rm -rf virtualenv

