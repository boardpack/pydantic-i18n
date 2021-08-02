#!/usr/bin/env bash

set -e
set -x

bash ./scripts/lint.sh
pytest --cov=pydantic_i18n --cov=tests --cov-report=term-missing --cov-report=xml tests ${@}
