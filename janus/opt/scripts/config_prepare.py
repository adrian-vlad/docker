#!/usr/bin/env python3

from jinja2 import Template
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
    "janus_port_streaming_start": int(os.environ["JANUS_PORT_STREAMING_START"])
}

#TODO: error on duplicated keys
# load the streaming configuration
with open(vars["streaming_config_file_path"], "r") as f:
    streaming_config = yaml.safe_load(f)

    # add ID to each stream because it will be used to create port numbers
    idx = 1
    for key, value in streaming_config.items():
        value["id"] = idx
        idx += 1

    vars["streaming_config"] = streaming_config

template_file_list = [
    #TODO: janus.jcfg port
    # Janus plugins
    "/etc/janus/janus.plugin.streaming.jcfg",

    # supervisor configuration files
    "/etc/supervisor/conf.d/process_listener.conf",
    "/etc/supervisor/conf.d/janus.conf",
    "/etc/supervisor/conf.d/ffmpeg_live_stream.conf",
    "/etc/supervisor/conf.d/live_streaming.conf",
    "/etc/supervisor/conf.d/nginx.conf",
]

for template in template_file_list:
    install_config_file_from_template(template, vars)

sys.exit(0)
