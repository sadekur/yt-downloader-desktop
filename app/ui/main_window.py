"""Main application window."""
from __future__ import annotations

import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.core.downloader import DownloadWorker, FetchFormatsWorker, FormatOption
from app.ui.theme import stylesheet_for

DEFAULT_OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "Downloads")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YT Downloader")
        self.resize(560, 320)

        self.output_dir = DEFAULT_OUTPUT_DIR
        self.formats: list[FormatOption] = []
        self.fetch_worker: FetchFormatsWorker | None = None
        self.download_worker: DownloadWorker | None = None

        self._build_ui()
        self._apply_theme(dark_mode=False)

    # -- UI construction -------------------------------------------------

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(10)

        # URL row
        url_row = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste YouTube URL here...")
        self.fetch_button = QPushButton("Fetch")
        self.fetch_button.clicked.connect(self.on_fetch_clicked)
        url_row.addWidget(self.url_input)
        url_row.addWidget(self.fetch_button)
        layout.addLayout(url_row)

        self.title_label = QLabel("")
        self.title_label.setWordWrap(True)
        layout.addWidget(self.title_label)

        # Quality row
        quality_row = QHBoxLayout()
        quality_row.addWidget(QLabel("Quality:"))
        self.quality_combo = QComboBox()
        self.quality_combo.setEnabled(False)
        quality_row.addWidget(self.quality_combo, stretch=1)
        layout.addLayout(quality_row)

        # Output folder row
        folder_row = QHBoxLayout()
        folder_row.addWidget(QLabel("Save to:"))
        self.folder_input = QLineEdit(self.output_dir)
        self.folder_input.setReadOnly(True)
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.on_browse_clicked)
        folder_row.addWidget(self.folder_input, stretch=1)
        folder_row.addWidget(browse_button)
        layout.addLayout(folder_row)

        # Action buttons row
        action_row = QHBoxLayout()
        self.download_video_button = QPushButton("Download Video")
        self.download_video_button.setEnabled(False)
        self.download_video_button.clicked.connect(lambda: self.start_download("video"))
        self.download_audio_button = QPushButton("Download Audio (MP3)")
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

        # Dark mode toggle
        self.dark_mode_checkbox = QCheckBox("Dark mode")
        self.dark_mode_checkbox.toggled.connect(self._apply_theme)
        layout.addWidget(self.dark_mode_checkbox, alignment=Qt.AlignRight)

    # -- Theme -------------------------------------------------------------

    def _apply_theme(self, dark_mode: bool) -> None:
        self.setStyleSheet(stylesheet_for(dark_mode))

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
