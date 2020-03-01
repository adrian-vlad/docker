#!/usr/bin/env python3

from jinja2 import Template
import json
import os
import sys
import yaml

janus_port_streaming_start = int(os.environ["JANUS_PORT_STREAMING_START"])
streaming_config_file_path = os.environ["STREAMING_CFG_PATH"]
janus_cfg_streaming_file_path = os.path.join(os.environ["JANUS_CFG_DIR"], "janus.plugin.streaming.jcfg")

# load the streaming configuration
with open(streaming_config_file_path, "r") as f:
    streaming_config = yaml.safe_load(f)

with open(janus_cfg_streaming_file_path + ".j2") as f:
    template = Template(f.read())

with open(janus_cfg_streaming_file_path, "w") as f:
    f.write(template.render(streaming_config=streaming_config, janus_port_streaming_start=janus_port_streaming_start))

sys.exit(0)
