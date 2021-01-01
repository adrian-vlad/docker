#!/bin/bash

set -e

# prepare janus configs
python3 /opt/scripts/init.py

# start supervisor
exec supervisord -c /etc/supervisor/supervisord.conf
