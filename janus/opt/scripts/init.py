#!/usr/bin/env python3

import os
import sys

from jinja2 import Template

from app.storage import get_enabled_cameras, initialize_storage
from default import ENV_VAR_RECORDINGS_DIR_PATH


def install_config_file_from_template(conf_file_path, vars_dict):
    with open(conf_file_path + ".j2") as f:
        tpl = Template(f.read())
    with open(conf_file_path, "w") as f:
        f.write(tpl.render(vars_dict))


initialize_storage()

template_vars = {
    "janus_port_streaming_start": int(os.environ["JANUS_PORT_STREAMING_START"]),
    "recordings_dir_path": os.environ[ENV_VAR_RECORDINGS_DIR_PATH],
    "cameras": get_enabled_cameras(),
}

template_file_list = [
    # TODO: janus.jcfg port
    # Janus plugins
    "/etc/janus/janus.plugin.streaming.jcfg",
    # supervisor configuration files
    "/etc/supervisor/conf.d/listener.conf",
    "/etc/supervisor/conf.d/janus.conf",
    "/etc/supervisor/conf.d/recorder.conf",
    "/etc/supervisor/conf.d/live.conf",
    "/etc/supervisor/conf.d/nginx.conf",
    "/etc/supervisor/conf.d/cron.conf",
]

for template in template_file_list:
    install_config_file_from_template(template, template_vars)

sys.exit(0)
