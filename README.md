# YT Downloader Desktop

A desktop YouTube downloader built with Python, PySide6 (Qt), and yt-dlp.

![YT Downloader icon](app/resources/icon-128.png)

## Features

- Paste a YouTube URL and fetch available qualities
- Download video (merged with best audio, output as MP4)
- Download audio only (converted to MP3 via ffmpeg)
- Choose the output folder
- Live download progress
- Dark mode toggle
- Preferences (default save folder, default theme) — persisted between runs
- Proper app icon and menu/dock entry, with "New Window" and "Preferences" quick actions

## Requirements

- Python 3.10+
- [ffmpeg](https://ffmpeg.org/) installed and available on your `PATH` (required for merging video/audio and MP3 extraction)

Install ffmpeg if you don't have it:

```bash
# Ubuntu / Debian
sudo apt install ffmpeg

# macOS (Homebrew)
brew install ffmpeg

# Windows (winget)
winget install Gyan.FFmpeg
```

## Installation (step by step)

1. **Get the code**

   ```bash
   git clone https://github.com/sadekur/yt-downloader-desktop.git
   cd yt-downloader-desktop
   ```

2. **Create a virtual environment and install dependencies**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate      # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Run the app**

   ```bash
   python main.py
   ```

   The app window should open — no account, no sign-up, no cost.

4. **(Optional, Linux) Add it to your app menu / dock**

   This registers a real launcher with its own icon and right-click actions
   (New Window, Preferences), instead of a generic "python3" entry:

   ```bash
   ./scripts/install_desktop_entry.sh
   ```

   After running it, search for "YT Downloader" in your applications menu, or
   pin it to your dock/taskbar.

## How to use the app

1. **Paste a YouTube URL** into the input box at the top (e.g.
   `https://www.youtube.com/watch?v=...`).
2. Click **Fetch** — the video title loads and the *Quality* dropdown fills
   with the available resolutions/formats for that video.
3. Pick a quality from the dropdown (only used for video downloads).
4. Click **Browse...** next to *Save to* if you want a different output
   folder than the default (`~/Downloads`).
5. Click **⬇ Download Video** to save the video (merged with best audio,
   MP4), or **♪ Download Audio (MP3)** to save just the audio track.
6. Watch the progress bar and status line — when it says "Done: ...", the
   file is in your chosen folder.
7. Use the **☾ / ☀** button in the header to toggle dark mode, and the
   **⚙** button to open **Preferences**, where you can set a default save
   folder and default theme so you don't have to pick them every time.

No YouTube login, API key, or payment is required — everything runs locally
using `yt-dlp` and `ffmpeg`.

## Troubleshooting

- **"Fetch failed" / no formats show up** — check your internet connection,
  and make sure the URL is a valid, public YouTube video link.
- **Download finishes but the file won't play, or download fails during
  merging** — make sure `ffmpeg` is installed and on your `PATH` (run
  `ffmpeg -version` in a terminal to check).
- **App icon shows as a generic icon in your dock** — run
  `./scripts/install_desktop_entry.sh` (Linux) and re-pin the app.

## Project structure

```
main.py                          # entry point (supports --preferences flag)
app/
  core/
    downloader.py                # yt-dlp integration (format lookup + download workers)
  ui/
    main_window.py               # main window / widgets
    preferences_dialog.py        # Preferences dialog (QSettings-backed)
    theme.py                     # light/dark stylesheets
  resources/
    icon.png, icon-*.png         # app icon at various sizes
scripts/
  generate_icon.py               # regenerates the app icon
  install_desktop_entry.sh       # installs the Linux app-menu/dock launcher
```
