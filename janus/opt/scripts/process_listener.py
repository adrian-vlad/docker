#!/usr/bin/python3

import datetime
import os
import subprocess
import sys
import traceback
from pathlib import Path

from pymediainfo import MediaInfo
from supervisor import childutils
from supervisor.childutils import listener

from app.storage import (
    add_video_file,
    get_enabled_cameras,
    get_max_total_size,
    get_video_file_names,
    get_video_files_time_ordered,
    remove_video_file,
)
from default import ENV_VAR_RECORDINGS_DIR_PATH, MAX_TOTAL_SIZE_PERCENT
from utils import start_time_from_file_name


CONFIG = {}


def write_stderr(s):
    sys.stderr.write(s)
    sys.stderr.flush()


def log(s):
    write_stderr(
        "[supervisor][process_listener.py]"
        + str(datetime.datetime.today())
        + " "
        + s
        + "\n"
    )


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


def create_new_recording_dirs():
    recordings_dir_path = os.environ[ENV_VAR_RECORDINGS_DIR_PATH]
    for camera in get_enabled_cameras():
        for i in range(0, 7):
            str_date = (datetime.date.today() + datetime.timedelta(days=i)).strftime(
                "%Y_%m_%d"
            )
            dir_path = os.path.join(recordings_dir_path, camera["name"], str_date)
            if not os.path.isdir(dir_path):
                os.makedirs(dir_path, exist_ok=True)


def cleanup_drive_space():
    files = get_video_files_time_ordered()

    total_size = 0
    for file in files:
        total_size += file["size"]

    max_total_size = int(get_max_total_size())

    base_directory = os.environ[ENV_VAR_RECORDINGS_DIR_PATH]

    while total_size >= max_total_size * MAX_TOTAL_SIZE_PERCENT / 100:
        file = files.pop(0)

        os.unlink(
            os.path.join(
                base_directory, file["camera_name"], file["directory"], file["name"]
            )
        )

        total_size -= file["size"]

        remove_video_file(file["camera_name"], file["name"])

        debug(f"Removed file {file['name']} for camera {file['camera_name']}")

        # TODO: remove directory, but only if it's older than today


def sync_video_files():
    base_directory = os.environ[ENV_VAR_RECORDINGS_DIR_PATH]

    for camera in get_enabled_cameras():
        camera_name = camera["name"]

        disk_video_files = [
            f
            for f in Path(os.path.join(base_directory, camera_name)).glob("**/*")
            if f.is_file()
        ]

        db_video_file_names = get_video_file_names(camera_name)

        # add files existing on the disk to the database
        for f in disk_video_files:
            file_name = f.name

            if file_name in db_video_file_names:
                db_video_file_names.remove(file_name)
                continue

            dir_name = f.parent.name
            start_time = start_time_from_file_name(file_name)

            durations = [
                track.duration
                for track in MediaInfo.parse(f).tracks
                if track.track_type == "Video"
            ]
            if durations:
                duration = int(durations[0])
            else:
                err(f"File {f} is not a video file; deleting")
                f.unlink()

                continue

            end_time = start_time + duration
            size = f.stat().st_size

            add_video_file(camera_name, file_name, dir_name, start_time, end_time, size)

        # remove files from the database that don't exist on the disk
        for file_name in db_video_file_names:
            remove_video_file(camera_name, file_name)

        # TODO: remove directories, but only those older than today


def process_state_fatal(payload):
    pheaders, pdata = childutils.eventdata(payload + "\n")
    groupName = pheaders["groupname"]

    # restart the whole group
    err("fatal " + groupName)
    supervisor_group_restart(groupName)


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


def process_event(msg_hdr, msg_payload):
    if msg_hdr["eventname"] == "PROCESS_STATE_FATAL":
        process_state_fatal(msg_payload)
    if msg_hdr["eventname"] == "TICK_60":
        process_tick60()


def main():
    # TODO: these should go in a different process
    create_new_recording_dirs()

    sync_video_files()

    cleanup_drive_space()

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
