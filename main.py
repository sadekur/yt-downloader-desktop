"""Entry point for the YT Downloader desktop app."""
import argparse
import os
import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from app.ui.main_window import MainWindow
from app.ui.preferences_dialog import PreferencesDialog, load_dark_mode
from app.ui.theme import apply_theme

ICON_PATH = os.path.join(os.path.dirname(__file__), "app", "resources", "icon.png")


def main() -> None:
    parser = argparse.ArgumentParser(description="YT Downloader desktop app")
    parser.add_argument(
        "--preferences",
        action="store_true",
        help="Open the Preferences dialog directly (used by the desktop launcher action)",
    )
    args = parser.parse_args()

    app = QApplication(sys.argv)
    app.setApplicationName("YT Downloader")
    app.setOrganizationName("YTDownloaderDesktop")
    app.setDesktopFileName("yt-downloader-desktop")
    app.setWindowIcon(QIcon(ICON_PATH))
    apply_theme(app, load_dark_mode())

    if args.preferences:
        dialog = PreferencesDialog()
        dialog.exec()
        return

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
