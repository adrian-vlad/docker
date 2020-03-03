#!/usr/bin/env python3

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
    "scripts_dir_path": os.environ["SCRIPTS_DIR_PATH"],
    "janus_bin_path": os.environ["JANUS_BIN_PATH"],
    "janus_port_streaming_start": int(os.environ["JANUS_PORT_STREAMING_START"]),
    "janus_cfg_streaming_file_path": os.path.join(os.environ["JANUS_CFG_DIR"], "janus.plugin.streaming.jcfg"),
    "supervisor_cfg_dir_path": os.environ["SUPERVISOR_CFG_DIR_PATH"]
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

#TODO: janus.jcfg port
# Janus plugins
install_config_file_from_template(vars["janus_cfg_streaming_file_path"], vars)

# Supervisor conf files
install_config_file_from_template(os.path.join(vars["supervisor_cfg_dir_path"], "conf.d", "process_listener.conf"), vars)
install_config_file_from_template(os.path.join(vars["supervisor_cfg_dir_path"], "conf.d", "janus.conf"), vars)
install_config_file_from_template(os.path.join(vars["supervisor_cfg_dir_path"], "conf.d", "ffmpeg.conf"), vars)
install_config_file_from_template(os.path.join(vars["supervisor_cfg_dir_path"], "conf.d", "web_server.conf"), vars)


sys.exit(0)
