#!/bin/bash
# Wrapper script to run sqlfluff fix from the virtual environment
source "$(dirname "$0")/../.venv/bin/activate"
sqlfluff fix --dialect duckdb "$@"
