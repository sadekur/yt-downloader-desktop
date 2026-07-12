#!/usr/bin/env bash
# Downloads the Windows ffmpeg/ffprobe binaries bundled into the .exe by
# packaging/windows.spec, so end users don't need to install ffmpeg
# separately. Not checked into git (~200MB) -- re-run whenever
# vendor/ffmpeg-windows is missing. Called automatically by
# scripts/build_windows_via_wine.sh. (Windows-native equivalent:
# scripts/fetch_ffmpeg_windows.ps1.)
#
# Source: Gyan Doshi's "essentials" Windows builds, mirrored on GitHub
# Releases (much faster than gyan.dev directly). ffmpeg is GPL-licensed;
# see https://github.com/GyanD/codexffmpeg for full source/build scripts.
set -euo pipefail

FFMPEG_VERSION="8.1.2"
URL="https://github.com/GyanD/codexffmpeg/releases/download/${FFMPEG_VERSION}/ffmpeg-${FFMPEG_VERSION}-essentials_build.zip"

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENDOR_DIR="$PROJECT_ROOT/vendor/ffmpeg-windows"

if [[ -f "$VENDOR_DIR/ffmpeg.exe" && -f "$VENDOR_DIR/ffprobe.exe" ]]; then
    echo "ffmpeg already present at $VENDOR_DIR, skipping download."
    exit 0
fi

mkdir -p "$VENDOR_DIR"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

echo "Downloading $URL ..."
curl -sL -o "$TMP_DIR/ffmpeg.zip" "$URL" --max-time 300

unzip -q "$TMP_DIR/ffmpeg.zip" -d "$TMP_DIR/extract"
BIN_DIR="$(find "$TMP_DIR/extract" -type d -name bin | head -1)"
cp "$BIN_DIR/ffmpeg.exe" "$VENDOR_DIR/ffmpeg.exe"
cp "$BIN_DIR/ffprobe.exe" "$VENDOR_DIR/ffprobe.exe"

echo "ffmpeg.exe / ffprobe.exe ready at $VENDOR_DIR"
