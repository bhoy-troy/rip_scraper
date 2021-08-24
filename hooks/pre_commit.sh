#!/usr/bin/env bash

PIPENV_VERBOSITY=-1

pipenv lock -r > images/python_rip/requirements.txt

isort rip

black rip