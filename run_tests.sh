#!/bin/bash
# Simple test runner that fixes Python import paths

cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH}:./event:./common"
python3 -m pytest tests/unit/ -v "$@"