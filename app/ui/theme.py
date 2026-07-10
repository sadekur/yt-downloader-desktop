"""Theme switching via qt-material (Material Design) — no hand-written stylesheets."""
from __future__ import annotations

from qt_material import apply_stylesheet

DARK_THEME = "dark_purple.xml"
LIGHT_THEME = "light_purple.xml"


def apply_theme(app, dark_mode: bool) -> None:
    theme = DARK_THEME if dark_mode else LIGHT_THEME
    apply_stylesheet(app, theme=theme, invert_secondary=not dark_mode)
