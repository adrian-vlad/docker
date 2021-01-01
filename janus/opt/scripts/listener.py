#!/usr/bin/python3

import datetime
import subprocess
import sys
import traceback

from supervisor.childutils import listener, eventdata


def write_stderr(s):
    sys.stderr.write(s)
    sys.stderr.flush()


def log(s):
    write_stderr(f"[supervisor][listener.py]{datetime.datetime.today()} {s}" + "\n")


def debug(s):
    log("[DEBUG] " + s)


def info(s):
    log("[INFO] " + s)


def err(s):
    log("[ERR] " + s)


def supervisor_restart(process_name):
    info(f"supervisorctl restarting {process_name}")
    subprocess.call(["supervisorctl", "restart", process_name], stdout=2, stderr=2)


def supervisor_group_restart(group_name):
    supervisor_restart(group_name + ":")


def process_state_fatal(payload):
    pheaders, pdata = eventdata(payload + "\n")
    group_name = pheaders["groupname"]

    # restart the whole group
    err(f"fatal {group_name}")
    supervisor_group_restart(group_name)


def process_event(msg_hdr, msg_payload):
    if msg_hdr["eventname"] == "PROCESS_STATE_FATAL":
        process_state_fatal(msg_payload)


def main():
    # run main loop
    while True:
        try:
            msg_hdr, msg_payload = listener.wait(sys.stdin, sys.stdout)

            if "eventname" in msg_hdr:
                process_event(msg_hdr, msg_payload)
        except KeyboardInterrupt:
            break
        except Exception as e:
            traceback.print_exc(file=sys.stderr)
            err(str(e))

        listener.ok(sys.stdout)


if __name__ == "__main__":
    main()
