"""A single row in the Recent Downloads list: thumbnail + title, click to open its folder."""
from __future__ import annotations

import os

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QFont, QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QMessageBox, QVBoxLayout

THUMB_W, THUMB_H = 100, 56


def _load_thumbnail(path: str) -> QPixmap | None:
    if not path or not os.path.exists(path):
        return None
    pixmap = QPixmap(path)
    if pixmap.isNull():
        return None
    scaled = pixmap.scaled(THUMB_W, THUMB_H, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
    x = max(0, (scaled.width() - THUMB_W) // 2)
    y = max(0, (scaled.height() - THUMB_H) // 2)
    return scaled.copy(x, y, THUMB_W, THUMB_H)


class DownloadItemWidget(QFrame):
    """Clickable card showing a completed download; click anywhere to open its folder."""

    def __init__(self, record: dict, parent=None):
        super().__init__(parent)
        self.record = record
        self.setFrameShape(QFrame.StyledPanel)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip("Click to open containing folder")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)

        thumb_label = QLabel()
        thumb_label.setFixedSize(THUMB_W, THUMB_H)
        thumb_label.setAlignment(Qt.AlignCenter)
        pixmap = _load_thumbnail(record.get("thumbnail_path", ""))
        if pixmap is not None:
            thumb_label.setPixmap(pixmap)
        else:
            thumb_label.setText("♪" if record.get("mode") == "audio" else "▶")
            placeholder_font = QFont()
            placeholder_font.setPointSize(20)
            thumb_label.setFont(placeholder_font)
        layout.addWidget(thumb_label)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)

        title_label = QLabel(record.get("title", "Untitled"))
        title_label.setWordWrap(True)
        title_font = QFont()
        title_font.setBold(True)
        title_label.setFont(title_font)
        text_col.addWidget(title_label)

        mode_text = "Audio (MP3)" if record.get("mode") == "audio" else "Video"
        subtitle = QLabel(f"{mode_text} · {os.path.basename(record.get('filepath', ''))}")
        subtitle.setWordWrap(True)
        text_col.addWidget(subtitle)

        layout.addLayout(text_col, stretch=1)

        open_hint = QLabel("📂 Open folder")
        open_hint.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(open_hint)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self._open_folder()
        super().mousePressEvent(event)

    def _open_folder(self) -> None:
        folder = os.path.dirname(self.record.get("filepath", ""))
        if folder and os.path.isdir(folder):
            QDesktopServices.openUrl(QUrl.fromLocalFile(folder))
        else:
            QMessageBox.warning(
                self,
                "Folder not found",
                f"Could not find:\n{folder}\n\nThe file may have been moved or deleted.",
            )
