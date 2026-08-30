# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A desktop YouTube downloader: Python + PySide6 (Qt) for the UI, yt-dlp for
fetching/downloading, ffmpeg for merging video/audio and MP3 extraction, and
`qt-material` for Material Design theming (no hand-written stylesheets/QSS).

## Commands

```bash
# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run
python main.py                # normal launch
python main.py --preferences  # open Preferences dialog directly (used by desktop launcher action)

# Linux: install/refresh the app-menu/dock launcher (regenerates the .desktop file)
./scripts/install_desktop_entry.sh

# Regenerate the app icon set (app/resources/icon*.png, icon.ico)
python scripts/generate_icon.py

# Build a full Windows installer: dist\installer\YT-Downloader-Setup.exe
# (must run ON Windows — no cross-compiling)
pip install -r requirements-build.txt
scripts\build_windows.bat
# Pipeline: fetch_ffmpeg_windows.ps1 (vendors ffmpeg.exe/ffprobe.exe) ->
# pyinstaller packaging/windows.spec (produces dist/YT Downloader.exe,
# ffmpeg bundled in) -> ISCC packaging/installer.iss (wraps it in an
# Inno Setup 6 installer)

# Cross-build that same Windows installer from Linux/macOS via Wine
# (fallback when no Windows machine is available; see the script's header
# for one-time system deps)
./scripts/build_windows_via_wine.sh
```

There is no test suite, linter, or formatter configured in this repo (no
pytest, no `pyproject.toml`/`setup.cfg` tooling section). Verify changes by
running the app (`python main.py`) and exercising the fetch/download flow
manually.

`ffmpeg` must be on `PATH` for merging (video downloads) and MP3 extraction
(audio downloads) to succeed when running from source (`python main.py`) —
required at runtime, not a build dependency. The packaged Windows installer
is the exception: it bundles `ffmpeg.exe`/`ffprobe.exe` directly (see
`_bundled_ffmpeg_dir()` below), so installed users need nothing on `PATH`.

## Architecture

Three-layer split, all wired together in `app/ui/main_window.py`:

- **`app/core/downloader.py`** — all yt-dlp interaction. Two `QThread`
  subclasses do the real work off the UI thread:
  - `FetchFormatsWorker` resolves a URL via `yt_dlp.extract_info(download=False)`
    and emits `(title, list[FormatOption])`. `_build_format_options` buckets
    formats by nearest standard resolution (`_STANDARD_HEIGHTS`, within 40px),
    keeping one best format per bucket — preferring `mp4` (to match
    `merge_output_format="mp4"`), then higher bitrate — so the quality
    dropdown shows one clean entry per standard resolution.
  - `DownloadWorker` runs the actual download. Video mode requests
    `f"{format_id}+bestaudio/best"` and merges to MP4 via
    `merge_output_format`; audio mode requests `bestaudio/best` and pipes
    through the `FFmpegExtractAudio` postprocessor to MP3. Progress is
    reported through yt-dlp's `progress_hooks` → Qt `progress` signal
    (percent, or `-1` for indeterminate when total size is unknown).
  - Thumbnails are downloaded once and cached to disk under Qt's
    `CacheLocation` (`_cache_thumbnail`), keyed by video ID, and referenced
    by local path afterward (not re-fetched from the network).
  - `_bundled_ffmpeg_dir()` points yt-dlp at a bundled `ffmpeg`/`ffprobe`
    when running as a PyInstaller-frozen build (`sys.frozen` + `sys._MEIPASS`);
    in dev mode it's a no-op and yt-dlp falls back to `PATH`.

- **`app/core/history.py`** — recent-downloads persistence via `QSettings`
  (`YTDownloaderDesktop`/`YTDownloader`), storing a JSON-encoded list capped
  at `MAX_HISTORY` (15) entries, newest first.

- **`app/ui/`** — `MainWindow` owns the worker threads (`fetch_worker`,
  `download_worker`) and wires their signals to UI updates; it never blocks
  on yt-dlp calls directly. `DownloadItemWidget` renders one history row
  (thumbnail + title, click-to-open-containing-folder). `PreferencesDialog`
  and `theme.py` both read/write the same `QSettings` store used by
  `history.py` — `output_dir` and `dark_mode` are the two persisted prefs,
  and `apply_theme()` swaps the whole app's `qt-material` stylesheet
  (`dark_purple.xml` / `light_purple.xml`) rather than any per-widget
  styling.

- **`main.py`** — entry point. Applies the saved theme before creating any
  window, and supports `--preferences` (used by the Linux desktop launcher's
  "Preferences" quick action) to open just the dialog instead of the main
  window.

- **`packaging/windows.spec`** — PyInstaller spec for producing a
  single-file `dist/YT Downloader.exe` (invoked by `scripts/build_windows.bat`).
  Explicitly bundles `app/resources`, `qt_material`'s package data (theme
  XML/fonts, via `collect_data_files`), the PySide6 Qt plugin DLLs (found via
  `importlib.util.find_spec` rather than importing `PySide6.QtCore`, which
  fails under Wine — see the comment in `_pyside6_plugin_binaries`), and
  `vendor/ffmpeg-windows/{ffmpeg,ffprobe}.exe` (fetched by
  `scripts/fetch_ffmpeg_windows.ps1`/`.sh`, gitignored, ~200MB) into an
  `ffmpeg/` folder inside the bundle.
- **`packaging/installer.iss`** — Inno Setup 6 script that wraps
  `dist/YT Downloader.exe` into `dist/installer/YT-Downloader-Setup.exe`, a
  per-user installer (no admin/UAC prompt) with Start Menu/Desktop shortcuts
  and an uninstaller entry. Compiled by `scripts/build_windows.bat` via
  `ISCC.exe`.
- **`scripts/build_windows_via_wine.sh`** — cross-builds the same installer
  from Linux/macOS by running a real Windows Python + PyInstaller + Inno
  Setup entirely under Wine (`WINEPREFIX`, default `~/.wine-ytdl-build`).
  Only needed when no Windows machine is available; `build_windows.bat` run
  natively on Windows is the simpler path.

## Conventions worth preserving

- No hand-written QSS/stylesheets — all theming goes through `qt-material`
  in `app/ui/theme.py`.
- Long-running yt-dlp calls always go through a `QThread` worker with
  `finished_ok`/`failed` signals, never called synchronously from a UI
  event handler.
- All persisted state (prefs, history) goes through `QSettings` under the
  `YTDownloaderDesktop`/`YTDownloader` org/app name — use the existing
  `get_settings()`/load/save helpers rather than instantiating `QSettings`
  ad hoc.
