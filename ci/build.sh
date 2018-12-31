#! /usr/bin/env sh
. ci/_setup_shell_env

pipenv run python setup.py bdist_wheel
