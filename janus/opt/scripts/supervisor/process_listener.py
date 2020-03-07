#!/usr/bin/python

import datetime
import json
import os
import subprocess
from supervisor.childutils import listener
from supervisor import childutils
import sys


def write_stderr(s):
    sys.stderr.write(s)
    sys.stderr.flush()
def log(s):
    write_stderr("[supervisor][process_listener.py]" + str(datetime.datetime.today()) + " " + s + "\n")
def debug(s):
    log("[DEBUG] " + s)
def info(s):
    log("[INFO] " + s)
def err(s):
    log("[ERR] " + s)


def supervisor_restart(process_name):
    info("supervisorctl restarting " + process_name)
    subprocess.call(["supervisorctl", "restart", process_name], stdout=2, stderr=2)


def supervisor_group_restart(groupName):
    supervisor_restart(groupName + ":")


def rtsp_stream_is_alive(stream_uri):
    openrtsp_path = "/opt/live555/openRTSP"
    try:
        openrtsp_cmd = openrtsp_path + " -v -d 1 " + stream_uri + " 2> /dev/null | wc -l"
        #debug("running '" + openrtsp_cmd + "'")
        out = subprocess.check_output(openrtsp_cmd, shell=True)
        if int(out) == 0:
            # stream does not work
            return False
    except Exception as e:
        err(str(e))
        return False

    return True


def process_state_fatal(payload):
    pheaders, pdata = childutils.eventdata(payload + "\n")
    groupName = pheaders["groupname"]

    # restart the whole group
    err("fatal " + groupName)
    supervisor_group_restart(groupName)


g_ticks = -1
def process_tick5():
    global g_ticks
    g_ticks = (g_ticks + 1) % 2
    if g_ticks != 0:
        # do stuff only once every 10 seconds
        return

    # check if streams are alive
    with open("/etc/streaming.json") as f:
        streaming_config = json.load(f)

    live555_port_start = int(os.environ["LIVE555_PORT_STREAMING_START"])

    for name, config in streaming_config["camera"].items():
        if not rtsp_stream_is_alive("rtsp://localhost:" + str(live555_port_start + config["id"]) + "/proxyStream"):
            err("stream not live for " + name)
            supervisor_group_restart(name)


def process_event(msg_hdr, msg_payload):
    if msg_hdr["eventname"] == "PROCESS_STATE_FATAL":
        process_state_fatal(msg_payload)
    if msg_hdr["eventname"] == "TICK_5":
        process_tick5()


def main():
    while True:
        try:
            msg_hdr, msg_payload = listener.wait(sys.stdin, sys.stdout)

            if "eventname" in msg_hdr:
                process_event(msg_hdr, msg_payload)

            listener.ok(sys.stdout)
        except KeyboardInterrupt:
            break
        except Exception as e:
            write_stderr(str(e))

if __name__ == '__main__':
    main()