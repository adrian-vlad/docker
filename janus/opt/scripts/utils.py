__all__ = ["start_time_from_file_name", "dir_name_from_file_name"]


def start_time_from_file_name(file_name: str) -> int:
    return int(file_name.split("_")[0])


def dir_name_from_file_name(file_name: str) -> str:
    return file_name.split("_")[1].replace("-", "_")
