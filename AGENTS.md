# AGENTS.md

## What this is

Python desktop app: PySide6 (Qt) + yt-dlp + qt-material (Material Design themes). No backend server, no API keys — everything runs locally.

## Run

```bash
python main.py                  # normal launch
python main.py --preferences    # open Preferences dialog directly
```

Requires a venv with `pip install -r requirements.txt`. Also requires `ffmpeg` on PATH.

## Build Windows installer

Must run **on Windows** (PyInstaller cannot cross-compile):

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt -r requirements-build.txt
scripts\build_windows.bat
```

Requires Inno Setup 6 installed (for `ISCC.exe`). The build fetches ffmpeg binaries automatically into `vendor/` (gitignored). Output: `dist\installer\YT-Downloader-Setup.exe`.

## Code structure

- `main.py` — entry point, argparse, QApplication setup
- `app/core/downloader.py` — yt-dlp integration (format lookup + download workers)
- `app/core/history.py` — recent-downloads persistence via QSettings
- `app/ui/main_window.py` — main window and widgets
- `app/ui/theme.py` — applies qt-material themes (no hand-written stylesheets)
- `app/ui/preferences_dialog.py` — preferences backed by QSettings
- `scripts/generate_icon.py` — regenerates app icons including `app/resources/icon.ico`

## Conventions

- Theming: use `qt-material` — do not add custom QSS stylesheets. Theme constants are in `app/ui/theme.py`.
- State persistence: QSettings (used for preferences and download history).
- No tests, no linter config, no CI, no typecheck — this is a small single-developer project.
- Runtime deps: `PySide6>=6.6`, `yt-dlp>=2024.1.1`, `qt-material>=2.14`. Build adds `pyinstaller>=6.0`.
