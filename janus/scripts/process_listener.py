#!/usr/bin/python

import os
import sys
from supervisor.childutils import listener
from supervisor import childutils
from subprocess import call
import datetime


def write_stderr(s):
    sys.stderr.write(s)
    sys.stderr.flush()
def log(s):
    write_stderr(str(datetime.datetime.today()) + " " + s + "\n")
def debug(s):
    log("[DEBUG] " + s)
def info(s):
    log("[INFO] " + s)
def err(s):
    log("[ERR] " + s)

def supervisor_restart(process_name):
    info("supervisorctl restarting " + process_name)
    with open(os.devnull, "w") as f:
        call(["supervisorctl", "restart", process_name], stdout=2, stderr=2)

def process_state_fatal(payload):
    pheaders, pdata = childutils.eventdata(payload + "\n")
    process_name = pheaders["processname"]

    err("fatal " + process_name)

    supervisor_restart(process_name)

def process_event(msg_hdr, msg_payload):
    if msg_hdr["eventname"] == "PROCESS_STATE_FATAL":
        process_state_fatal(msg_payload)

def main():
    while True:
        try:
            msg_hdr, msg_payload = listener.wait(sys.stdin, sys.stdout)

            if "eventname" in msg_hdr:
                process_event(msg_hdr, msg_payload)

            listener.ok(sys.stdout)
        except Exception as e:
            write_stderr(str(e))

if __name__ == '__main__':
    main()