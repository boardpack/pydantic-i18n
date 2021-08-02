#!/usr/bin/env bash

set -e
set -x

mypy pydantic_i18n
flake8 pydantic_i18n tests
black pydantic_i18n tests --check
isort pydantic_i18n tests scripts --check-only
