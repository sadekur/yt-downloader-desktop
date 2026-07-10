"""Preferences dialog backed by QSettings (persisted across runs)."""
from __future__ import annotations

import os

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

DEFAULT_OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "Downloads")


def get_settings() -> QSettings:
    return QSettings("YTDownloaderDesktop", "YTDownloader")


def load_output_dir() -> str:
    return get_settings().value("output_dir", DEFAULT_OUTPUT_DIR, type=str)


def load_dark_mode() -> bool:
    return get_settings().value("dark_mode", False, type=bool)


def save_output_dir(path: str) -> None:
    get_settings().setValue("output_dir", path)


def save_dark_mode(enabled: bool) -> None:
    get_settings().setValue("dark_mode", enabled)


class PreferencesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(10)

        folder_row = QHBoxLayout()
        self.folder_input = QLineEdit(load_output_dir())
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self._on_browse)
        folder_row.addWidget(self.folder_input)
        folder_row.addWidget(browse_button)
        form.addRow("Default save folder:", folder_row)

        self.dark_mode_checkbox = QCheckBox("Enable dark mode")
        self.dark_mode_checkbox.setChecked(load_dark_mode())
        form.addRow("Appearance:", self.dark_mode_checkbox)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_browse(self) -> None:
        chosen = QFileDialog.getExistingDirectory(self, "Select default folder", self.folder_input.text())
        if chosen:
            self.folder_input.setText(chosen)

    def _on_save(self) -> None:
        save_output_dir(self.folder_input.text().strip() or DEFAULT_OUTPUT_DIR)
        save_dark_mode(self.dark_mode_checkbox.isChecked())
        self.accept()
