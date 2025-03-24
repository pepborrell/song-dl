from pathlib import Path

import yt_dlp


def url_to_mp3(url: str, download_dir: Path) -> Path:
    output_file = {"path": None}

    def download_hook(d: dict):
        print(f"{d=}")
        if d["status"] == "finished":
            output_file["path"] = d["filename"]  # Capture final path

    ydl_opts = {
        "paths": {"home": str(download_dir)},  # Set custom download folder
        "outtmpl": "%(title)s.%(ext)s",  # Only filename, path is set via `paths`
        "extract_flat": "discard_in_playlist",
        "final_ext": "mp3",
        "format": "bestaudio/best",
        "fragment_retries": 10,
        "ignoreerrors": "only_download",
        "nooverwrites": False,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "nopostoverwrites": False,
                "preferredcodec": "mp3",
                "preferredquality": "0",
            },
            {"key": "FFmpegConcat", "only_multi_video": True, "when": "playlist"},
        ],
        "retries": 10,
        "progress_hooks": [download_hook],
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download([url])

    if error_code != 0:
        raise Exception(f"Download failed with error code {error_code}")

    output_path = output_file["path"]
    assert output_path is not None, "Output path not set"

    # Because yt-dlp doesn't set the extension correctly.
    return Path(output_path).with_suffix(".mp3")


def get_video_title(url: str):
    ydl_opts = {
        "quiet": True,
        "noplaylist": True,  # Ensure it's a single video, not a playlist
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info.get("title", "Unknown Title")
