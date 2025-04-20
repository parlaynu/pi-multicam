#!/usr/bin/env bash

RUN_DIR="$( dirname "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" )"
cd ${RUN_DIR}

export PYTHONPATH=${RUN_DIR}
pytest -v tests/unit
# pytest -s -v .
