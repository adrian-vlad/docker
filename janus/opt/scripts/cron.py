import datetime
import os
import signal
import sys
import time
from pathlib import Path

from pymediainfo import MediaInfo
import schedule

from app.storage import (
    add_video_file,
    get_enabled_cameras,
    get_max_total_size,
    get_video_file_names,
    get_video_files_time_ordered,
    remove_video_file,
)
from app.utils import start_time_from_file_name
from default import ENV_VAR_RECORDINGS_DIR_PATH, MAX_TOTAL_SIZE_PERCENT


g_shutdown = False


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


def sync_video_files():
    base_directory = os.environ[ENV_VAR_RECORDINGS_DIR_PATH]

    for camera in get_enabled_cameras():
        camera_name = camera["name"]
        segment_time = int(camera["segment_time"])

        disk_video_files = [
            f
            for f in Path(os.path.join(base_directory, camera_name)).glob("**/*")
            if f.is_file()
        ]

        db_video_file_names = get_video_file_names(camera_name)

        # add files existing on the disk to the database
        for f in disk_video_files:
            if g_shutdown:
                return

            file_name = f.name

            if file_name in db_video_file_names:
                db_video_file_names.remove(file_name)
                continue

            dir_name = f.parent.name
            start_time = start_time_from_file_name(file_name)

            if start_time + segment_time * 2 > time.time():
                # this might be an in progress video; skip it
                continue

            durations = [
                track.duration
                for track in MediaInfo.parse(f).tracks
                if track.track_type == "Video"
            ]
            if durations:
                duration = int(durations[0])
            else:
                print(f"File {f} is not a video file; deleting", file=sys.stderr)
                f.unlink()

                continue

            end_time = start_time + duration
            size = f.stat().st_size

            add_video_file(camera_name, file_name, dir_name, start_time, end_time, size)

        # remove files from the database that don't exist on the disk
        for file_name in db_video_file_names:
            remove_video_file(camera_name, file_name)

        # TODO: remove directories, but only those older than today


def cleanup_drive_space():
    files = get_video_files_time_ordered()

    total_size = 0
    for file in files:
        total_size += file["size"]

    max_total_size = int(get_max_total_size())

    base_directory = os.environ[ENV_VAR_RECORDINGS_DIR_PATH]

    while total_size >= max_total_size * MAX_TOTAL_SIZE_PERCENT / 100:
        if g_shutdown:
            return

        file = files.pop(0)

        os.unlink(
            os.path.join(
                base_directory, file["camera_name"], file["directory"], file["name"]
            )
        )

        total_size -= file["size"]

        remove_video_file(file["camera_name"], file["name"])

        print(
            f"Removed file {file['name']} for camera {file['camera_name']}", flush=True
        )

        # TODO: remove directory, but only if it's older than today


def job():
    # create new directories for the new days to store video files
    create_new_recording_dirs()

    # make sure that what is on disk it's also in the database
    sync_video_files()

    # remove older videos if space available becomes small
    cleanup_drive_space()


def main():
    schedule.every(10).minutes.do(job)
    schedule.run_all()

    def signal_handler(sig, frame):
        if sig == signal.SIGINT or sig == signal.SIGTERM:
            global g_shutdown
            g_shutdown = True

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    while not g_shutdown:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
