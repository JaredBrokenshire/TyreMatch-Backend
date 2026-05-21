import os
from policies import uuid_filename

BASE_FILE_DIRECTORY = "/files"

def allowed_file(filename: str, valid_extensions: list[str]) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1] in valid_extensions

def save_file(file, upload_dir: str, valid_extensions: list[str]) -> str:
    if not file or file.filename == "":
        raise ValueError("File cannot be empty")

    if not allowed_file(file.filename, valid_extensions):
        raise ValueError("File type not allowed")

    dir = os.path.join(BASE_FILE_DIRECTORY, upload_dir)

    os.makedirs(dir, exist_ok=True)

    path = os.path.join(dir, file.filename)

    file.save(path)

    return path