#!/bin/bash

set -e

# prepare janus configs
python3 /opt/scripts/config_prepare.py

# start supervisor
exec supervisord -c /etc/supervisor/supervisord.conf
