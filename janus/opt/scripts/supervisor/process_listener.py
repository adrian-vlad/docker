#!/usr/bin/python3

import datetime
import json
import os
from pathlib import Path
from pymediainfo import MediaInfo
import subprocess
from supervisor.childutils import listener
from supervisor import childutils
import sys


CONFIG = {}


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
        out = subprocess.check_output(openrtsp_cmd, shell=True)
        if int(out) == 0:
            # stream does not work
            return False
    except Exception as e:
        err(str(e))
        return False

    return True


def create_new_recording_dirs():
    recordings_dir_path = os.environ["RECORDINGS_DIR_PATH"]
    for name, config in CONFIG["camera"].items():
        for i in range(0, 7):
            str_date = (datetime.date.today() + datetime.timedelta(days=i)).strftime('%Y_%m_%d')
            dir_path = os.path.join(recordings_dir_path, name, str_date)
            if not os.path.isdir(dir_path):
                os.makedirs(dir_path, exist_ok=True)


def cleanup_drive_space():
    files = sorted(
        [f for f in Path(os.environ["RECORDINGS_DIR_PATH"]).glob('**/*') if f.is_file()],
        key=lambda f: f.name
    )

    dir_size = sum(f.stat().st_size for f in files)

    while dir_size >= CONFIG["limit_disk_space"]:
        file_to_delete = files.pop(0)
        parent_directory = file_to_delete.parent

        dir_size -= file_to_delete.stat().st_size

        file_to_delete.unlink()
        debug("removed file " + str(file_to_delete))

        # delete empty directories
        try:
            parent_directory.rmdir()
            debug("removed directory " + str(parent_directory))
        except OSError:
            pass


def create_videos_list():
    base_directory = os.environ["RECORDINGS_DIR_PATH"]
    database_path = os.path.join(base_directory, "recordings.json")

    try:
        with open(database_path) as f:
            database = json.load(f)
    except Exception:
        # TODO: specific exception
        database = {
            "lowest_timestamp": 2**64,
            "highest_timestamp": 0,
            "cameras": {cam_name: {"files": []} for cam_name in CONFIG["camera"]}
        }
    # force updating lowest timestamp to account for files that have been deleted due to regular cleanup
    database["lowest_timestamp"] = 2**64

    for cam_name in CONFIG["camera"]:
        uri_prefix = "static/recordings"

        recording_files = [f for f in Path(os.path.join(base_directory, cam_name)).glob("**/*") if f.is_file()]
        for f in recording_files:
            file_path = os.path.join(base_directory, cam_name, str(f))
            uri = os.path.join(uri_prefix, file_path[(len(base_directory) + len(os.path.sep)):])

            entry = {
                "path": uri,
                "duration": 0,
                "timestamp": int(f.name.split("_")[0]) * 1000,
                "mtime": os.path.getmtime(file_path)
            }

            skip_file = False
            for old_entry in database["cameras"][cam_name]["files"]:
                if entry["path"] == old_entry["path"]:
                    if entry["mtime"] == old_entry["mtime"]:
                        # file has not been modified since last inspection; we can skip it
                        skip_file = True
                    else:
                        # the file has been modified and the duration need to be rechecked
                        database["cameras"][cam_name]["files"].remove(old_entry)

                    break

            # updated the lowest timestamp
            if database["lowest_timestamp"] > entry["timestamp"]:
                database["lowest_timestamp"] = entry["timestamp"]

            if skip_file:
                continue

            durations = [track.duration for track in MediaInfo.parse(file_path).tracks if track.track_type == "Video"]
            if durations:
                entry["duration"] = int(durations[0])
            else:
                # this might not be a video file
                continue

            database["cameras"][cam_name]["files"].append(entry)

            # update the highest timestamp
            if database["highest_timestamp"] < entry["timestamp"] + entry["duration"]:
                database["highest_timestamp"] = entry["timestamp"] + entry["duration"]

    with open(database_path, "w") as f:
        f.write(json.dumps(database, indent=2))


def process_state_fatal(payload):
    pheaders, pdata = childutils.eventdata(payload + "\n")
    groupName = pheaders["groupname"]

    # restart the whole group
    err("fatal " + groupName)
    supervisor_group_restart(groupName)


g_ticks_10_sec = -1
def process_tick5():
    global g_ticks_10_sec
    g_ticks_10_sec = (g_ticks_10_sec + 1) % 2
    if g_ticks_10_sec != 0:
        # do stuff only once every 10 seconds
        return

    # check if streams are alive
    live555_port_start = int(os.environ["LIVE555_PORT_STREAMING_START"])

    for name, config in CONFIG["camera"].items():
        if not rtsp_stream_is_alive("rtsp://localhost:" + str(live555_port_start + config["id"]) + "/proxyStream"):
            err("stream not live for " + name)
            supervisor_group_restart(name)


g_ticks_10_min = -1
def process_tick60():
    global g_ticks_10_min
    g_ticks_10_min = (g_ticks_10_min + 1) % 10
    if g_ticks_10_min != 0:
        # do stuff only once every 10 minutes
        return

    # create new directories for the new days to store video files
    create_new_recording_dirs()

    # remove older videos if space available becomes small
    cleanup_drive_space()

    # create the list of videos to be loaded by the web server
    create_videos_list()


def process_event(msg_hdr, msg_payload):
    if msg_hdr["eventname"] == "PROCESS_STATE_FATAL":
        process_state_fatal(msg_payload)
    if msg_hdr["eventname"] == "TICK_5":
        process_tick5()
    if msg_hdr["eventname"] == "TICK_60":
        process_tick60()


def main():
    # load the configuration
    with open("/etc/streaming.json") as f:
        global CONFIG
        CONFIG = json.load(f)

    create_new_recording_dirs()

    # run main loop
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
