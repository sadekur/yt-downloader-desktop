#!/usr/bin/env bash
# Installs a .desktop launcher for this app into the current user's applications
# menu, so it shows up with its own icon, name, and right-click actions
# (New Window / Preferences) instead of a generic "python3" entry.
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PYTHON="$PROJECT_DIR/.venv/bin/python"
ICON_PATH="$PROJECT_DIR/app/resources/icon.png"
APPS_DIR="$HOME/.local/share/applications"
DESKTOP_FILE="$APPS_DIR/yt-downloader-desktop.desktop"

mkdir -p "$APPS_DIR"

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=YT Downloader
Comment=Download YouTube videos and audio
Exec=$VENV_PYTHON $PROJECT_DIR/main.py
Icon=$ICON_PATH
Terminal=false
Categories=AudioVideo;Network;
StartupWMClass=yt-downloader-desktop
Actions=NewWindow;Preferences;

[Desktop Action NewWindow]
Name=New Window
Exec=$VENV_PYTHON $PROJECT_DIR/main.py

[Desktop Action Preferences]
Name=Preferences
Exec=$VENV_PYTHON $PROJECT_DIR/main.py --preferences
EOF

chmod +x "$DESKTOP_FILE"

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APPS_DIR" >/dev/null 2>&1 || true
fi

echo "Installed: $DESKTOP_FILE"
echo "You may need to unpin/re-pin or log out-in for the dock to fully refresh."
