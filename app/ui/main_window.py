"""Main application window."""
from __future__ import annotations

import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from app.core.downloader import DownloadWorker, FetchFormatsWorker, FormatOption
from app.ui.preferences_dialog import PreferencesDialog, load_dark_mode, load_output_dir, save_dark_mode
from app.ui.theme import apply_theme

RESOURCES_DIR = os.path.join(os.path.dirname(__file__), "..", "resources")
ICON_PATH = os.path.join(RESOURCES_DIR, "icon.png")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YT Downloader")
        self.setWindowIcon(QIcon(ICON_PATH))
        self.resize(620, 420)

        self.output_dir = load_output_dir()
        self.dark_mode = load_dark_mode()
        self.formats: list[FormatOption] = []
        self.fetch_worker: FetchFormatsWorker | None = None
        self.download_worker: DownloadWorker | None = None

        self._build_ui()
        self._apply_theme()

    # -- UI construction -------------------------------------------------

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())

        body = QWidget()
        layout = QVBoxLayout(body)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(14)
        root.addWidget(body)

        # URL row
        url_row = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste YouTube URL here...")
        self.fetch_button = QPushButton("Fetch")
        self.fetch_button.setObjectName("fetchButton")
        self.fetch_button.setCursor(Qt.PointingHandCursor)
        self.fetch_button.clicked.connect(self.on_fetch_clicked)
        url_row.addWidget(self.url_input)
        url_row.addWidget(self.fetch_button)
        layout.addLayout(url_row)

        self.title_label = QLabel("")
        self.title_label.setObjectName("titleLabel")
        self.title_label.setWordWrap(True)
        layout.addWidget(self.title_label)

        # Options card: quality + output folder
        options_card = QFrame()
        options_card.setObjectName("card")
        options_layout = QVBoxLayout(options_card)
        options_layout.setSpacing(10)

        quality_row = QHBoxLayout()
        quality_row.addWidget(QLabel("Quality:"))
        self.quality_combo = QComboBox()
        self.quality_combo.setEnabled(False)
        quality_row.addWidget(self.quality_combo, stretch=1)
        options_layout.addLayout(quality_row)

        folder_row = QHBoxLayout()
        folder_row.addWidget(QLabel("Save to:"))
        self.folder_input = QLineEdit(self.output_dir)
        self.folder_input.setReadOnly(True)
        browse_button = QPushButton("Browse...")
        browse_button.setObjectName("browseButton")
        browse_button.setCursor(Qt.PointingHandCursor)
        browse_button.clicked.connect(self.on_browse_clicked)
        folder_row.addWidget(self.folder_input, stretch=1)
        folder_row.addWidget(browse_button)
        options_layout.addLayout(folder_row)

        layout.addWidget(options_card)

        # Action buttons row
        action_row = QHBoxLayout()
        action_row.setSpacing(12)
        self.download_video_button = QPushButton("⬇  Download Video")
        self.download_video_button.setObjectName("videoButton")
        self.download_video_button.setCursor(Qt.PointingHandCursor)
        self.download_video_button.setEnabled(False)
        self.download_video_button.clicked.connect(lambda: self.start_download("video"))
        self.download_audio_button = QPushButton("♪  Download Audio (MP3)")
        self.download_audio_button.setObjectName("audioButton")
        self.download_audio_button.setCursor(Qt.PointingHandCursor)
        self.download_audio_button.setEnabled(False)
        self.download_audio_button.clicked.connect(lambda: self.start_download("audio"))
        action_row.addWidget(self.download_video_button)
        action_row.addWidget(self.download_audio_button)
        layout.addLayout(action_row)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("statusLabel")
        layout.addWidget(self.status_label)

        layout.addStretch(1)

    def _build_header(self) -> QFrame:
        header = QFrame()
        header.setObjectName("headerBar")
        header.setFixedHeight(56)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 8, 16, 8)
        header_layout.setSpacing(10)

        icon_label = QLabel()
        icon_label.setPixmap(QPixmap(ICON_PATH).scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header_layout.addWidget(icon_label)

        title = QLabel("YT Downloader")
        title.setObjectName("headerTitle")
        header_layout.addWidget(title)

        header_layout.addStretch(1)

        self.theme_button = QToolButton()
        self.theme_button.setObjectName("headerIconButton")
        self.theme_button.setCursor(Qt.PointingHandCursor)
        self.theme_button.setToolTip("Toggle dark mode")
        self.theme_button.clicked.connect(self.on_theme_toggle_clicked)
        header_layout.addWidget(self.theme_button)

        settings_button = QToolButton()
        settings_button.setObjectName("headerIconButton")
        settings_button.setText("⚙")
        settings_button.setCursor(Qt.PointingHandCursor)
        settings_button.setToolTip("Preferences")
        settings_button.clicked.connect(self.on_preferences_clicked)
        header_layout.addWidget(settings_button)

        return header

    # -- Theme -------------------------------------------------------------

    def _apply_theme(self) -> None:
        self.setStyleSheet(stylesheet_for(self.dark_mode))
        self.theme_button.setText("☀" if self.dark_mode else "☾")

    def on_theme_toggle_clicked(self) -> None:
        self.dark_mode = not self.dark_mode
        save_dark_mode(self.dark_mode)
        self._apply_theme()

    def on_preferences_clicked(self) -> None:
        dialog = PreferencesDialog(self)
        if dialog.exec():
            self.output_dir = load_output_dir()
            self.folder_input.setText(self.output_dir)
            self.dark_mode = load_dark_mode()
            self._apply_theme()

    # -- Fetch formats -------------------------------------------------------

    def on_fetch_clicked(self) -> None:
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Missing URL", "Please paste a YouTube URL first.")
            return

        self.fetch_button.setEnabled(False)
        self.download_video_button.setEnabled(False)
        self.download_audio_button.setEnabled(False)
        self.quality_combo.clear()
        self.quality_combo.setEnabled(False)
        self.title_label.setText("")
        self.status_label.setText("Fetching video info...")

        self.fetch_worker = FetchFormatsWorker(url)
        self.fetch_worker.finished_ok.connect(self.on_fetch_finished)
        self.fetch_worker.failed.connect(self.on_fetch_failed)
        self.fetch_worker.start()

    def on_fetch_finished(self, title: str, formats: list[FormatOption]) -> None:
        self.fetch_button.setEnabled(True)
        self.title_label.setText(title)
        self.formats = formats

        video_formats = [f for f in formats if not f.is_audio_only]
        self.quality_combo.clear()
        for fmt in video_formats:
            self.quality_combo.addItem(fmt.label, userData=fmt.format_id)
        self.quality_combo.setEnabled(bool(video_formats))

        self.download_video_button.setEnabled(bool(video_formats))
        self.download_audio_button.setEnabled(True)
        self.status_label.setText("Ready to download.")

    def on_fetch_failed(self, message: str) -> None:
        self.fetch_button.setEnabled(True)
        self.status_label.setText("Failed to fetch video info.")
        QMessageBox.critical(self, "Fetch failed", message)

    # -- Output folder -------------------------------------------------------

    def on_browse_clicked(self) -> None:
        chosen = QFileDialog.getExistingDirectory(self, "Select output folder", self.output_dir)
        if chosen:
            self.output_dir = chosen
            self.folder_input.setText(chosen)

    # -- Download -------------------------------------------------------

    def start_download(self, mode: str) -> None:
        url = self.url_input.text().strip()
        if not url:
            return

        format_id = None
        if mode == "video":
            format_id = self.quality_combo.currentData()

        self._set_controls_enabled(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting download...")

        self.download_worker = DownloadWorker(
            url=url,
            output_dir=self.output_dir,
            mode=mode,
            format_id=format_id,
        )
        self.download_worker.progress.connect(self.on_download_progress)
        self.download_worker.finished_ok.connect(self.on_download_finished)
        self.download_worker.failed.connect(self.on_download_failed)
        self.download_worker.start()

    def on_download_progress(self, percent: int, text: str) -> None:
        if percent < 0:
            self.progress_bar.setRange(0, 0)  # indeterminate
        else:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(percent)
        self.status_label.setText(text)

    def on_download_finished(self, filepath: str) -> None:
        self._set_controls_enabled(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        self.status_label.setText(f"Done: {os.path.basename(filepath)}")

    def on_download_failed(self, message: str) -> None:
        self._set_controls_enabled(True)
        self.status_label.setText("Download failed.")
        QMessageBox.critical(self, "Download failed", message)

    def _set_controls_enabled(self, enabled: bool) -> None:
        self.fetch_button.setEnabled(enabled)
        self.download_video_button.setEnabled(enabled and bool(self.quality_combo.count()))
        self.download_audio_button.setEnabled(enabled)
