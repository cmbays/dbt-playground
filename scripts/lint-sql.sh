#!/bin/bash
# Wrapper script to run sqlfluff from the virtual environment
source "$(dirname "$0")/../.venv/bin/activate"
sqlfluff lint --dialect duckdb "$@"
