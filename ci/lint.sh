#! /usr/bin/env sh
. ci/_setup_shell_env

pipenv run mystubs
pipenv run mypy src
