import fcntl
import logging
import os
import signal
import subprocess
import sys
import time

import prctl
from pymediainfo import MediaInfo

from app.storage import add_video_file, get_camera
from app.utils import dir_name_from_file_name, start_time_from_file_name
from default import ENV_VAR_JANUS_RTP_START_PORT, ENV_VAR_RECORDINGS_DIR_PATH


recordings_dir_path = os.environ[ENV_VAR_RECORDINGS_DIR_PATH]
janus_rtp_start_port = int(os.environ[ENV_VAR_JANUS_RTP_START_PORT])

camera_name = sys.argv[1]
camera = get_camera(camera_name)

# prepare ffmpeg command
cmd_args = [
    "/usr/bin/stdbuf",
    "-o0",
    "-e0",
    "/usr/bin/ffmpeg",
    "-nostats",
    "-loglevel",
    "+level+warning",
    "-rtsp_transport",
    camera["transport"],
    "-i",
    camera["url"],
    "-f",
    "segment",
    "-metadata",
    f"title={camera_name}",
    "-c",
    "copy",
    "-an",
    "-flags",
    "+global_header",
    "-segment_list",
    f"pipe:1",
    "-segment_time",
    f"{camera['segment_time']}",
    "-segment_atclocktime",
    "1",
    "-reset_timestamps",
    "1",
    "-segment_format",
    "mp4",
    "-segment_format_options",
    # used fragmented mp4 to eliminate the recording gaps created by the second pass for faststart
    "moov_size=2000000",
    "-strftime",
    "1",
    "-y",
    f"{recordings_dir_path}/{camera_name}/%Y_%m_%d/%s_%Y-%m-%d_%H-%M-%S.mp4",
    "-f",
    "rtp",
    "-an",
    "-c:v",
    "copy",
    "-flags",
    "global_header",
    "-bsf",
    "dump_extra",
    f"rtp://localhost:{janus_rtp_start_port + camera['sequence']}",
]

# start the process and make stdout unblocking
p = subprocess.Popen(
    cmd_args,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    preexec_fn=lambda: prctl.set_pdeathsig(signal.SIGKILL),
)

fd = p.stdout.fileno()
fl = fcntl.fcntl(fd, fcntl.F_GETFL)
fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

g_shutdown = False


def signal_handler(sig, frame):
    if sig == signal.SIGINT or sig == signal.SIGTERM:
        p.stdin.writelines(["q".encode()])

        global g_shutdown
        g_shutdown = True


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def add_video(video_name: str) -> None:
    if len(video_name) <= 0:
        return

    video_name = video_name.strip()

    dir_name = dir_name_from_file_name(video_name)
    start_time = start_time_from_file_name(video_name)
    full_path = os.path.join(recordings_dir_path, camera_name, dir_name, video_name)

    durations = [
        track.duration
        for track in MediaInfo.parse(full_path).tracks
        if track.track_type == "Video"
    ]
    if durations:
        duration = int(durations[0]) / 1000
    else:
        logging.error(f"File {full_path} is not a video file; deleting")
        os.unlink(full_path)

        return

    end_time = start_time + duration
    size = os.stat(full_path).st_size

    add_video_file(
        camera_name,
        video_name,
        dir_name_from_file_name(video_name),
        start_time_from_file_name(video_name),
        end_time,
        size,
    )


while p.poll() is None:
    time.sleep(0.1)

    add_video(p.stdout.readline().decode())


output, _ = p.communicate()
for line in output.decode().splitlines():
    add_video(line)


if g_shutdown:
    sys.exit(0)
else:
    print(f"Subprocess stopped unexpectatly: {p.returncode}", file=sys.stderr)
    sys.exit(p.returncode)
