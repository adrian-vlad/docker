#!/usr/bin/env python3

import json
import os
import sys
import yaml

janus_port_streaming_start = int(os.environ["JANUS_PORT_STREAMING_START"])
streaming_config_file_path = os.environ["STREAMING_CFG_PATH"]
janus_cfg_streaming_file_path = os.path.join(os.environ["JANUS_CFG_DIR"], "janus.plugin.streaming.jcfg")

with open(streaming_config_file_path, "r") as f:
    streaming_config = yaml.safe_load(f)

janus_streaming_config = {}
janus_streaming_config["general"] = {}

idx = 1
for name, value in streaming_config.items():
    stream_config = {}
    stream_config["type"] = "rtp"
    stream_config["id"] = idx
    stream_config["description"] = name
    stream_config["audio"] = False
    stream_config["video"] = True
    stream_config["videoport"] = janus_port_streaming_start + idx
    stream_config["videopt"] = 96
    stream_config["videortpmap"] = "H264/90000"
    stream_config["videofmtp"] = "profile-level-id=42e028;packetization-mode=1"

    if name in janus_streaming_config:
        sys.stderr.write(f"Duplicate name: {name}\n")
        sys.exit(1)
    else:
        janus_streaming_config[name] = stream_config

    idx += 1

with open(janus_cfg_streaming_file_path, "w") as f:
    for name, value in janus_streaming_config.items():
        f.write(f"{name}: {{\n")

        for prop_name, prop_value in value.items():
            f.write(f"{prop_name} = {json.dumps(prop_value)}\n")

        f.write(f"}}\n")

sys.exit(0)
