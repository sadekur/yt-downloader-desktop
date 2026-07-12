#!/usr/bin/env bash
# Cross-builds the Windows installer (dist/installer/YT-Downloader-Setup.exe)
# from Linux/macOS, by running a real Windows Python + PyInstaller + Inno
# Setup entirely under Wine. This is a workaround for not having a Windows
# machine -- if you do have one, scripts/build_windows.bat run natively
# there is simpler and more reliable.
#
# One-time system requirements (need sudo, not handled by this script):
#   sudo dpkg --add-architecture i386
#   sudo apt-get update
#   sudo apt-get install -y wine64 wine wine32:i386 winetricks
#
# Everything else (Windows Python, pip deps, ffmpeg, Inno Setup) is fetched
# into $WINEPREFIX / vendor/ by this script and is safe to re-run.
#
# Env overrides: WINEPREFIX (default: ~/.wine-ytdl-build), PYTHON_VERSION.
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export WINEARCH=win64
export WINEPREFIX="${WINEPREFIX:-$HOME/.wine-ytdl-build}"
PYTHON_VERSION="${PYTHON_VERSION:-3.12.7}"
unset WINEDEBUG  # WINEDEBUG=-all breaks stdio handle setup for python.exe under Wine

# CPython's full startup (anything beyond `--version`) needs a real
# stdout/stderr handle; a plain pipe sometimes leaves Wine unable to hand
# Python a valid Windows HANDLE ("Fatal Python error: init_sys_streams").
# Allocating a pty via `script` avoids that reliably.
run_wine() {
    script -qec "$*" /tmp/build_windows_via_wine.pty.log < /dev/null
}

command -v wine >/dev/null || {
    echo "wine not found. Install it first:" >&2
    echo "  sudo dpkg --add-architecture i386 && sudo apt-get update && sudo apt-get install -y wine64 wine wine32:i386 winetricks" >&2
    exit 1
}

WINE_PYTHON='C:\Python312\python.exe'

if [[ ! -f "$WINEPREFIX/drive_c/Python312/python.exe" ]]; then
    echo "== Setting up Wine prefix and installing Windows Python $PYTHON_VERSION =="
    wineboot --init
    TMP_DIR="$(mktemp -d)"
    curl -sL -o "$TMP_DIR/python-installer.exe" \
        "https://www.python.org/ftp/python/${PYTHON_VERSION}/python-${PYTHON_VERSION}-amd64.exe" --max-time 120
    run_wine "wine '$TMP_DIR/python-installer.exe' /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 SimpleInstall=1 TargetDir='C:\\Python312'"
    rm -rf "$TMP_DIR"
fi

echo "== Installing/upgrading Python dependencies =="
run_wine "wine '$WINE_PYTHON' -m pip install --upgrade pip -q"
run_wine "cd '$PROJECT_ROOT' && wine '$WINE_PYTHON' -m pip install -r requirements.txt -r requirements-build.txt -q"

echo "== Fetching bundled ffmpeg =="
"$PROJECT_ROOT/scripts/fetch_ffmpeg_windows.sh"

echo "== Building app .exe with PyInstaller =="
rm -rf "$PROJECT_ROOT/dist" "$PROJECT_ROOT/build"
run_wine "cd '$PROJECT_ROOT' && wine '$WINE_PYTHON' -m PyInstaller packaging/windows.spec --noconfirm"

ISCC='C:\Program Files (x86)\Inno Setup 6\ISCC.exe'
if [[ ! -f "$WINEPREFIX/drive_c/Program Files (x86)/Inno Setup 6/ISCC.exe" ]]; then
    echo "== Installing Inno Setup =="
    TMP_DIR="$(mktemp -d)"
    curl -sL -o "$TMP_DIR/innosetup.exe" "https://jrsoftware.org/download.php/is.exe" --max-time 60
    run_wine "wine '$TMP_DIR/innosetup.exe' /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP-"
    rm -rf "$TMP_DIR"
fi

echo "== Compiling installer with Inno Setup =="
run_wine "cd '$PROJECT_ROOT' && wine '$ISCC' packaging\\\\installer.iss"

echo
echo "Build complete: dist/installer/YT-Downloader-Setup.exe"
file "$PROJECT_ROOT/dist/installer/YT-Downloader-Setup.exe"
