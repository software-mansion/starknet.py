import os


def file_from_directory(directory: str, filename: str) -> str:
    return os.path.join(directory, filename)
