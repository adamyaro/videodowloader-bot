import os
import uuid
from pathlib import Path

import yt_dlp

DOWNLOAD_FOLDER = Path("downloads")
DOWNLOAD_FOLDER.mkdir(exist_ok=True)


def download_video(url: str) -> str:
    file_id = str(uuid.uuid4())

    ydl_opts = {
        "outtmpl": str(DOWNLOAD_FOLDER / f"{file_id}.%(ext)s"),
        "format": "best",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

    if os.path.exists(filename):
        return filename

    for path in DOWNLOAD_FOLDER.glob(f"{file_id}.*"):
        return str(path)

    raise FileNotFoundError("Файл после скачивания не найден")