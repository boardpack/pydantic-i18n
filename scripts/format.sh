#!/bin/sh -e
set -x

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place pydantic_i18n tests scripts --exclude=__init__.py
black pydantic_i18n tests scripts
isort pydantic_i18n tests scripts
