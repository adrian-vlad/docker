#!/usr/bin/env python3

import json
import os

from flask import Flask, render_template, request

from app.storage import get_enabled_cameras, get_events, get_video_files


app = Flask(__name__)


@app.route("/<int:camera_id>/streaming.js", methods=["GET"])
def streaming_js(camera_id):
    ip = request.host.split(":")[0]
    return render_template("streaming.js.j2", camera_id=camera_id, ip=ip)


@app.route("/<int:camera_id>", methods=["GET"])
def streaming_html(camera_id):
    return render_template("streaming.html.j2", camera_id=camera_id)


@app.route("/recordings.json", methods=["GET"])
def recordings():
    lowest_timestamp = 2 ** 64
    highest_timestamp = 0
    cameras = {}

    uri_prefix = "static/recordings"

    for camera in get_enabled_cameras():
        files = []
        for file in get_video_files(camera["name"]):
            files.append(
                {
                    "path": os.path.join(
                        uri_prefix, camera["name"], file["directory"], file["name"]
                    ),
                    "start_time": file["start_time"] * 1000,
                    "end_time": file["end_time"] * 1000,
                }
            )

            if lowest_timestamp > file["start_time"]:
                lowest_timestamp = file["start_time"]
            if highest_timestamp < file["start_time"]:
                highest_timestamp = file["start_time"]

        events = []
        for event in get_events(camera["name"]):
            # TODO: need to delete the events from storage and rebuild the docker image
            if event["start_time"] < lowest_timestamp:
                continue

            events.append(
                {
                    "name": event["name"],
                    "start_time": event["start_time"] * 1000,
                    "end_time": event["end_time"] * 1000
                    if event["end_time"] is not None
                    else None,
                }
            )

        cameras[camera["name"]] = {"files": files, "events": events}

    return json.dumps(
        {
            "lowest_timestamp": lowest_timestamp * 1000,
            "highest_timestamp": highest_timestamp * 1000,
            "cameras": cameras,
        }
    )


if __name__ == "__main__":
    app.run()
