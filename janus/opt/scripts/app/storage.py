__all__ = [
    "initialize_storage",
    "get_max_total_size",
    "get_camera",
    "get_enabled_cameras",
    "get_video_file_names",
    "get_video_files_time_ordered",
    "add_video_file",
    "remove_video_file",
    "add_event",
    "get_events",
]

import os
from typing import Dict, List, Optional, Sequence

import yaml

from app.db import Reader, Writer
from default import DB_PATH, ENV_VAR_CONFIG_PATH


# TODO: voluptuous
# TODO: orm


def initialize_storage() -> None:
    config_path = os.environ[ENV_VAR_CONFIG_PATH]

    # TODO: error on duplicated keys
    # TODO: names should contain only alphanum and underscore
    # load the streaming configuration
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

        # add ID to each stream because it will be used to create port numbers
        idx = 1
        for key, value in config["camera"].items():
            value["id"] = idx
            idx += 1

    with Writer(DB_PATH) as db_write:
        db_write.write(
            " CREATE TABLE IF NOT EXISTS"
            " Config("
            "   name TEXT NOT NULL PRIMARY KEY,"
            "   value TEXT NOT NULL"
            ")"
        )

        db_write.write(
            " INSERT INTO Config (name, value)"
            " VALUES (?, ?)"
            " ON CONFLICT(Name) DO UPDATE "
            " SET value = ?",
            parameters=(
                "max_total_size",
                config["limit_disk_space"],
                config["limit_disk_space"],
            ),
        )

        db_write.write(
            " CREATE TABLE IF NOT EXISTS"
            " Camera("
            "   name TEXT NOT NULL PRIMARY KEY,"
            "   url TEXT NOT NULL,"
            "   sequence INTEGER NOT NULL,"
            "   transport TEXT NOT NULL,"
            "   segment_time INTEGER NOT NULL,"
            "   hik_url TEXT,"
            "   hik_user TEXT,"
            "   hik_pass TEXT,"
            "   enabled BOOLEAN NOT NULL"
            ")"
        )
        for camera, settings in config["camera"].items():
            url = settings["src"]
            order = settings["id"]
            transport = settings.get("rtsp_transport", "udp")
            segment_time = int(settings.get("segment_time", "900"))
            hik_url = None
            hik_user = None
            hik_pass = None
            if "hik" in settings:
                hik_url = settings["hik"].get("url", None)
                hik_user = settings["hik"].get("user", None)
                hik_pass = settings["hik"].get("pass", None)

            db_write.write(
                " INSERT INTO Camera ("
                "   name,"
                "   url,"
                "   sequence,"
                "   transport,"
                "   segment_time,"
                "   hik_url,"
                "   hik_user,"
                "   hik_pass,"
                "   enabled"
                ")"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)"
                " ON CONFLICT(name) DO UPDATE "
                " SET"
                " url = ?,"
                " sequence = ?,"
                " transport = ?,"
                " segment_time = ?,"
                " hik_url = ?,"
                " hik_user = ?,"
                " hik_pass = ?,"
                " enabled = 1",
                parameters=(
                    camera,
                    url,
                    order,
                    transport,
                    segment_time,
                    hik_url,
                    hik_user,
                    hik_pass,
                    url,
                    order,
                    transport,
                    segment_time,
                    hik_url,
                    hik_user,
                    hik_pass,
                ),
            )

        db_write.write(
            " CREATE TABLE IF NOT EXISTS"
            " Video("
            "   camera_name TEXT NOT NULL,"
            "   name TEXT NOT NULL,"
            "   directory TEXT NOT NULL,"
            "   start_time INTEGER NOT NULL,"
            "   end_time INTEGER NOT NULL,"
            "   size INTEGER NOT NULL,"
            "   PRIMARY KEY(camera_name, name)"
            ")"
        )

        db_write.write(
            " CREATE TABLE IF NOT EXISTS"
            " Event("
            "   camera_name TEXT NOT NULL,"
            "   name TEXT NOT NULL,"
            "   start_time INTEGER NOT NULL,"
            "   end_time INTEGER,"
            "   PRIMARY KEY(camera_name, name, start_time)"
            ")"
        )


def get_max_total_size() -> str:
    with Reader(DB_PATH) as db_read:
        return db_read.read(
            "SELECT value FROM Config WHERE name = ?", parameters=("max_total_size",)
        )[0]["value"]


def get_camera(camera_name: str) -> Dict:
    with Reader(DB_PATH) as db_read:
        return db_read.read(
            " SELECT url, sequence, transport, segment_time, hik_url, hik_user, hik_pass"
            " FROM Camera WHERE name = ?",
            parameters=(camera_name,),
        )[0]


def get_enabled_cameras() -> Sequence[Dict]:
    with Reader(DB_PATH) as db_read:
        return db_read.read(
            " SELECT name, url, sequence, transport, segment_time FROM Camera WHERE enabled = 1"
        )


def get_video_file_names(camera_name: str) -> List[str]:
    with Reader(DB_PATH) as db_read:
        files = db_read.read(
            " SELECT name FROM Video WHERE camera_name = ?",
            parameters=(camera_name,),
        )

        return [file["name"] for file in files]


def get_video_files(camera_name: str) -> Sequence[Dict]:
    with Reader(DB_PATH) as db_read:
        return db_read.read(
            " SELECT name, directory, start_time, end_time, size"
            " FROM Video "
            " WHERE camera_name = ?",
            parameters=(camera_name,),
        )


def get_video_files_time_ordered() -> Sequence[Dict]:
    with Reader(DB_PATH) as db_read:
        return db_read.read(
            " SELECT camera_name, name, directory, size FROM Video ORDER BY start_time ASC"
        )


def add_video_file(
    camera_name: str,
    file_name: str,
    dir_name: str,
    start_time: int,
    end_time: int,
    size: int,
) -> None:
    with Writer(DB_PATH) as db_write:
        db_write.write(
            " INSERT INTO Video (camera_name, name, directory, start_time, end_time, size)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            parameters=(camera_name, file_name, dir_name, start_time, end_time, size),
        )


def remove_video_file(camera_name: str, file_name: str) -> None:
    with Writer(DB_PATH) as db_write:
        db_write.write(
            " DELETE FROM Video WHERE camera_name = ? AND name = ?",
            parameters=(camera_name, file_name),
        )


def get_events(camera_name: str) -> Sequence[Dict]:
    with Reader(DB_PATH) as db_read:
        return db_read.read(
            " SELECT name, start_time, end_time"
            " FROM Event "
            " WHERE camera_name = ?",
            parameters=(camera_name,),
        )


def add_event(
    camera_name: str, name: str, start_time: int, end_time: Optional[int]
) -> None:
    with Writer(DB_PATH) as db_write:
        db_write.write(
            " INSERT INTO Event (camera_name, name, start_time, end_time)"
            " VALUES (?, ?, ?, ?)"
            " ON CONFLICT(camera_name, name, start_time) DO UPDATE "
            " SET"
            " end_time = ?",
            parameters=(camera_name, name, start_time, end_time, end_time),
        )
