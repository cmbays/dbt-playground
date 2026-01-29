#!/bin/bash
# Wrapper script to run yamllint from the virtual environment
source "$(dirname "$0")/../.venv/bin/activate"
yamllint -c .yamllint.yml "$@"
