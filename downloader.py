import os
import uuid
import yt_dlp

DOWNLOAD_FOLDER = "downloads"

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


async def download_video(url: str):
    file_id = str(uuid.uuid4())

    ydl_opts = {
        "outtmpl": f"{DOWNLOAD_FOLDER}/{file_id}.%(ext)s",
        "format": "best",
        "noplaylist": True,
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

    return filename