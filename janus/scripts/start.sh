#!/bin/bash

set -e

# prepare janus configs
python3 ${SCRIPTS_DIR_PATH}/config_prepare.py

# start supervisor
exec supervisord -c ${SUPERVISOR_CFG_DIR_PATH}/supervisord.conf
