import json
from pathlib import Path

from pydantic import BaseModel

from song_dl.paths import ALL_DOWNLOADS_FILE


class DownloadMetadata(BaseModel):
    url: str
    title: str
    source: str
    save_path: Path
    artist: str | None
    album: str | None


def get_all_downloads() -> dict[str, DownloadMetadata]:
    if not ALL_DOWNLOADS_FILE.exists():
        ALL_DOWNLOADS_FILE.parent.mkdir(parents=True, exist_ok=True)
        ALL_DOWNLOADS_FILE.touch(exist_ok=False)
        return {}
    with open(ALL_DOWNLOADS_FILE, "r") as f:
        downloads = [DownloadMetadata(**json.loads(line)) for line in f]
    return {d.url: d for d in downloads}


def add_download_data(metadata: DownloadMetadata):
    with open(ALL_DOWNLOADS_FILE, "a") as f:
        f.write(metadata.model_dump_json() + "\n")
