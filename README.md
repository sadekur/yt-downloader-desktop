# YT Downloader Desktop

A desktop YouTube downloader built with Python, PySide6 (Qt), and yt-dlp.

## Features

- Paste a YouTube URL and fetch available qualities
- Download video (merged with best audio, output as MP4)
- Download audio only (converted to MP3 via ffmpeg)
- Choose the output folder
- Live download progress
- Dark mode toggle

## Requirements

- Python 3.10+
- [ffmpeg](https://ffmpeg.org/) installed and available on your `PATH` (required for merging video/audio and MP3 extraction)

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Project structure

```
main.py                  # entry point
app/
  core/
    downloader.py        # yt-dlp integration (format lookup + download workers)
  ui/
    main_window.py        # main window / widgets
    theme.py               # light/dark stylesheets
```
