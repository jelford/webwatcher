#! /usr/bin/env sh
. ci/_setup_shell_env

pip install dist/webwatcher-$(cat ./version.txt)-py3-none-any.whl
pip install -r test-requirements.txt
