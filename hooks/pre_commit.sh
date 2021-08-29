#!/usr/bin/env bash

PIPENV_VERBOSITY=-1



isort --check rip
CHECK_CODE=$?

if [ ${CHECK_CODE} -eq 1 ]; then
  isort --atomic rip
fi

if [ ${CHECK_CODE} -eq 0 ]; then
  black --check rip
  CHECK_CODE=$?

  if  [ ${CHECK_CODE} -eq 1 ]; then
    black rip
  fi
fi

if [ ${CHECK_CODE} -eq 0 ]; then
  flake8 rip
  CHECK_CODE=$?
fi


if [ ${CHECK_CODE} -eq 0 ]; then
  pipenv lock -r > images/python_rip/requirements.txt
  CHECK_CODE=$?
fi


exit ${CHECK_CODE}
