#! /usr/bin/env sh
. ci/_setup_shell_env

pipenv run mypy src
