#!/usr/bin/env python3

import datetime
from jinja2 import Template
import json
import os
import sys
import yaml

def install_config_file_from_template(conf_file_path, vars_dict):
    with open(conf_file_path + ".j2") as f:
        template = Template(f.read())
    with open(conf_file_path, "w") as f:
        f.write(template.render(vars_dict))

vars = {
    "streaming_config_file_path": os.environ["STREAMING_CFG_PATH"],
    "janus_port_streaming_start": int(os.environ["JANUS_PORT_STREAMING_START"]),
    "recordings_dir_path": os.environ["RECORDINGS_DIR_PATH"]
}

#TODO: error on duplicated keys
#TODO: names should contain only alphanum and underscore
# load the streaming configuration
with open(vars["streaming_config_file_path"], "r") as f:
    streaming_config = yaml.safe_load(f)

    # add ID to each stream because it will be used to create port numbers
    idx = 1
    for key, value in streaming_config["camera"].items():
        value["id"] = idx
        idx += 1

    vars["streaming_config"] = streaming_config

template_file_list = [
    #TODO: janus.jcfg port
    # Janus plugins
    "/etc/janus/janus.plugin.streaming.jcfg",

    # supervisor configuration files
    "/etc/supervisor/conf.d/listener.conf",
    "/etc/supervisor/conf.d/janus.conf",
    "/etc/supervisor/conf.d/camera_processor.conf",
    "/etc/supervisor/conf.d/live_view_server.conf",
    "/etc/supervisor/conf.d/nginx.conf",
]

for template in template_file_list:
    install_config_file_from_template(template, vars)

# Save the streaming config on disk
with open("/etc/streaming.json", "w") as f:
    json.dump(vars["streaming_config"], f)

sys.exit(0)
