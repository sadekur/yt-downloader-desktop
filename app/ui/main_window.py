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
    QScrollArea,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from app.core.downloader import DownloadResult, DownloadWorker, FetchFormatsWorker, FormatOption
from app.core.history import add_to_history, load_history, remove_from_history
from app.ui.download_item import DownloadItemWidget
from app.ui.preferences_dialog import PreferencesDialog, load_dark_mode, load_output_dir, save_dark_mode
from app.ui.theme import apply_theme

RESOURCES_DIR = os.path.join(os.path.dirname(__file__), "..", "resources")
ICON_PATH = os.path.join(RESOURCES_DIR, "icon.png")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YT Downloader")
        self.setWindowIcon(QIcon(ICON_PATH))
        self.resize(640, 640)

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
        self.fetch_button.setCursor(Qt.PointingHandCursor)
        self.fetch_button.clicked.connect(self.on_fetch_clicked)
        url_row.addWidget(self.url_input)
        url_row.addWidget(self.fetch_button)
        layout.addLayout(url_row)

        self.title_label = QLabel("")
        title_font = QFont()
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setWordWrap(True)
        layout.addWidget(self.title_label)

        # Options card: quality + output folder
        options_card = QFrame()
        options_card.setFrameShape(QFrame.StyledPanel)
        options_card.setFrameShadow(QFrame.Raised)
        options_layout = QVBoxLayout(options_card)
        options_layout.setContentsMargins(12, 12, 12, 12)
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
        self.download_video_button.setCursor(Qt.PointingHandCursor)
        self.download_video_button.setEnabled(False)
        self.download_video_button.clicked.connect(lambda: self.start_download("video"))
        self.download_audio_button = QPushButton("♪  Download Audio (MP3)")
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
        layout.addWidget(self.status_label)

        layout.addWidget(self._build_downloads_section())

    def _build_downloads_section(self) -> QWidget:
        section = QWidget()
        section_layout = QVBoxLayout(section)
        section_layout.setContentsMargins(0, 8, 0, 0)
        section_layout.setSpacing(8)

        header = QLabel("Recent Downloads")
        header_font = QFont()
        header_font.setBold(True)
        header.setFont(header_font)
        section_layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(260)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        self.downloads_list_layout = QVBoxLayout(container)
        self.downloads_list_layout.setContentsMargins(0, 0, 0, 0)
        self.downloads_list_layout.setSpacing(8)
        self.downloads_list_layout.addStretch(1)
        scroll.setWidget(container)

        section_layout.addWidget(scroll)
        self._refresh_downloads_list(load_history())
        return section

    def _build_header(self) -> QFrame:
        header = QFrame()
        header.setFixedHeight(56)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 8, 16, 8)
        header_layout.setSpacing(10)

        icon_label = QLabel()
        icon_label.setPixmap(QPixmap(ICON_PATH).scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header_layout.addWidget(icon_label)

        title = QLabel("YT Downloader")
        title_font = QFont()
        title_font.setPointSize(title_font.pointSize() + 2)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)

        header_layout.addStretch(1)

        self.theme_button = QToolButton()
        self.theme_button.setCursor(Qt.PointingHandCursor)
        self.theme_button.setToolTip("Toggle dark mode")
        self.theme_button.clicked.connect(self.on_theme_toggle_clicked)
        header_layout.addWidget(self.theme_button)

        settings_button = QToolButton()
        settings_button.setText("⚙")
        settings_button.setCursor(Qt.PointingHandCursor)
        settings_button.setToolTip("Preferences")
        settings_button.clicked.connect(self.on_preferences_clicked)
        header_layout.addWidget(settings_button)

        return header

    # -- Downloads history -------------------------------------------------

    def _clear_downloads_layout(self) -> None:
        while self.downloads_list_layout.count() > 1:  # keep the trailing stretch
            item = self.downloads_list_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _refresh_downloads_list(self, history: list[dict]) -> None:
        self._clear_downloads_layout()
        if not history:
            placeholder = QLabel("No downloads yet — completed downloads will appear here.")
            placeholder.setAlignment(Qt.AlignCenter)
            self.downloads_list_layout.insertWidget(0, placeholder)
            return
        for record in history:
            item_widget = DownloadItemWidget(record)
            self.downloads_list_layout.insertWidget(self.downloads_list_layout.count() - 1, item_widget)

    # -- Theme -------------------------------------------------------------

    def _apply_theme(self) -> None:
        apply_theme(QApplication.instance(), self.dark_mode)
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

    def on_download_finished(self, result: DownloadResult) -> None:
        self._set_controls_enabled(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        self.status_label.setText(f"Done: {os.path.basename(result.filepath)}")

        record = {
            "title": result.title,
            "filepath": result.filepath,
            "thumbnail_path": result.thumbnail_path,
            "mode": result.mode,
        }
        history = add_to_history(record)
        self._refresh_downloads_list(history)

    def on_download_failed(self, message: str) -> None:
        self._set_controls_enabled(True)
        self.status_label.setText("Download failed.")
        QMessageBox.critical(self, "Download failed", message)

    def _set_controls_enabled(self, enabled: bool) -> None:
        self.fetch_button.setEnabled(enabled)
        self.download_video_button.setEnabled(enabled and bool(self.quality_combo.count()))
        self.download_audio_button.setEnabled(enabled)
