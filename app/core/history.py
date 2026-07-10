"""Persisted list of recently completed downloads (thumbnail + filepath)."""
from __future__ import annotations

import json

from PySide6.QtCore import QSettings

MAX_HISTORY = 15


def _settings() -> QSettings:
    return QSettings("YTDownloaderDesktop", "YTDownloader")


def load_history() -> list[dict]:
    raw = _settings().value("download_history", "[]", type=str)
    try:
        history = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return []
    return history if isinstance(history, list) else []


def add_to_history(record: dict) -> list[dict]:
    history = load_history()
    history.insert(0, record)
    history = history[:MAX_HISTORY]
    _settings().setValue("download_history", json.dumps(history))
    return history
