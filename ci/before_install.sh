#! /usr/bin/env sh
. ci/_setup_shell_env

pip install wheel
python setup.py bdist_wheel
