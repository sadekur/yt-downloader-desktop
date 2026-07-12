"""yt-dlp integration: format discovery and download workers."""
from __future__ import annotations

import os
import sys
import urllib.request
from dataclasses import dataclass

import yt_dlp
from PySide6.QtCore import QStandardPaths, QThread, Signal


def _bundled_ffmpeg_dir() -> str | None:
    """Directory holding a bundled ffmpeg/ffprobe when frozen via PyInstaller.

    The Windows build embeds ffmpeg.exe/ffprobe.exe under an "ffmpeg/" folder
    (see packaging/windows.spec) so end users don't need to install ffmpeg
    themselves. In dev mode (not frozen), yt-dlp falls back to PATH as usual.
    """
    if not getattr(sys, "frozen", False):
        return None
    candidate = os.path.join(sys._MEIPASS, "ffmpeg")
    exe_name = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
    return candidate if os.path.exists(os.path.join(candidate, exe_name)) else None


@dataclass
class FormatOption:
    format_id: str
    label: str
    ext: str
    is_audio_only: bool


@dataclass
class DownloadResult:
    title: str
    filepath: str
    thumbnail_path: str  # local cached path, "" if unavailable
    mode: str  # "video" or "audio"


def _thumbnail_cache_dir() -> str:
    base = QStandardPaths.writableLocation(QStandardPaths.CacheLocation) or "/tmp"
    cache_dir = os.path.join(base, "thumbnails")
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


def _cache_thumbnail(url: str | None, video_id: str) -> str:
    if not url or not video_id:
        return ""
    ext = os.path.splitext(url.split("?")[0])[1] or ".jpg"
    dest = os.path.join(_thumbnail_cache_dir(), f"{video_id}{ext}")
    if os.path.exists(dest):
        return dest
    try:
        urllib.request.urlretrieve(url, dest)
    except Exception:
        return ""
    return dest


def _human_size(num_bytes: float | None) -> str:
    if not num_bytes:
        return ""
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TB"


# Standard quality ladder shown in the UI, highest first. Raw formats are
# snapped to the nearest rung here rather than listed as-is, since a video
# typically has many near-duplicate formats (different codecs/bitrates/fps
# per resolution) that aren't a meaningful choice for most users.
_STANDARD_HEIGHTS = [2160, 1440, 1080, 720, 480, 360, 240, 144]


def _build_format_options(info: dict) -> list[FormatOption]:
    best_by_height: dict[int, dict] = {}

    for fmt in info.get("formats", []):
        height = fmt.get("height")
        if fmt.get("vcodec") == "none" or not height:
            continue

        bucket = min(_STANDARD_HEIGHTS, key=lambda h: abs(h - height))
        if abs(bucket - height) > 40:
            continue  # not close enough to a standard resolution to show

        current = best_by_height.get(bucket)
        if current is None:
            best_by_height[bucket] = fmt
            continue

        # Prefer mp4 sources (matches merge_output_format="mp4" on download);
        # otherwise prefer the higher-bitrate format at the same resolution.
        ext, current_ext = fmt.get("ext", ""), current.get("ext", "")
        if ext == "mp4" and current_ext != "mp4":
            best_by_height[bucket] = fmt
        elif ext == current_ext and (fmt.get("tbr") or 0) > (current.get("tbr") or 0):
            best_by_height[bucket] = fmt

    options = []
    for height in _STANDARD_HEIGHTS:
        fmt = best_by_height.get(height)
        if fmt is None:
            continue
        options.append(
            FormatOption(
                format_id=fmt["format_id"],
                label=f"{height}p - {fmt.get('ext', '')}",
                ext=fmt.get("ext", ""),
                is_audio_only=False,
            )
        )

    return options


class FetchFormatsWorker(QThread):
    """Resolves a URL to its title and available formats."""

    finished_ok = Signal(str, list)  # title, list[FormatOption]
    failed = Signal(str)

    def __init__(self, url: str, parent=None):
        super().__init__(parent)
        self.url = url

    def run(self) -> None:
        try:
            ydl_opts = {"quiet": True, "no_warnings": True, "skip_download": True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
        except Exception as exc:  # yt_dlp raises various DownloadError subclasses
            self.failed.emit(str(exc))
            return

        title = info.get("title", "Unknown title")
        options = _build_format_options(info)
        self.finished_ok.emit(title, options)


class DownloadWorker(QThread):
    """Downloads video or audio for a URL into an output directory."""

    progress = Signal(int, str)  # percent (0-100, -1 = indeterminate), status text
    finished_ok = Signal(object)  # DownloadResult
    failed = Signal(str)

    def __init__(
        self,
        url: str,
        output_dir: str,
        mode: str,  # "video" or "audio"
        format_id: str | None = None,
        parent=None,
    ):
        super().__init__(parent)
        self.url = url
        self.output_dir = output_dir
        self.mode = mode
        self.format_id = format_id
        self._last_filename = ""

    def _progress_hook(self, status: dict) -> None:
        if status["status"] == "downloading":
            total = status.get("total_bytes") or status.get("total_bytes_estimate")
            downloaded = status.get("downloaded_bytes", 0)
            if total:
                percent = int(downloaded / total * 100)
                text = f"Downloading... {percent}% ({_human_size(downloaded)} / {_human_size(total)})"
            else:
                percent = -1
                text = f"Downloading... {_human_size(downloaded)}"
            self.progress.emit(percent, text)
        elif status["status"] == "finished":
            self._last_filename = status.get("filename", "")
            self.progress.emit(100, "Processing...")

    def run(self) -> None:
        outtmpl = f"{self.output_dir}/%(title)s.%(ext)s"
        ydl_opts: dict = {
            "quiet": True,
            "no_warnings": True,
            "outtmpl": outtmpl,
            "progress_hooks": [self._progress_hook],
        }

        ffmpeg_dir = _bundled_ffmpeg_dir()
        if ffmpeg_dir:
            ydl_opts["ffmpeg_location"] = ffmpeg_dir

        if self.mode == "audio":
            ydl_opts["format"] = "bestaudio/best"
            ydl_opts["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ]
        else:
            fmt = self.format_id or "bestvideo"
            ydl_opts["format"] = f"{fmt}+bestaudio/best"
            ydl_opts["merge_output_format"] = "mp4"

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=True)
                filepath = ydl.prepare_filename(info)
                if self.mode == "audio":
                    filepath = filepath.rsplit(".", 1)[0] + ".mp3"
        except Exception as exc:
            self.failed.emit(str(exc))
            return

        thumbnail_path = _cache_thumbnail(info.get("thumbnail"), info.get("id", ""))
        result = DownloadResult(
            title=info.get("title", os.path.basename(filepath)),
            filepath=filepath,
            thumbnail_path=thumbnail_path,
            mode=self.mode,
        )
        self.finished_ok.emit(result)
