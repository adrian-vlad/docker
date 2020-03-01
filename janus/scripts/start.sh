#!/bin/bash

set -e

# prepare janus configs
python3 ${SCRIPTS_DIR_PATH}/config_prepare.py

# start janus
exec ${JANUS_BIN_PATH}
