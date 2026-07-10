"""Light/dark stylesheets for the app."""

ACCENT_FROM = "#7C3AED"   # violet
ACCENT_TO = "#2563EB"     # blue
WARM_FROM = "#FF5F6D"     # coral
WARM_TO = "#FFC371"       # amber

_SHARED = f"""
QFrame#headerBar {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {ACCENT_FROM}, stop:1 {ACCENT_TO});
    border: none;
}}
QLabel#headerTitle {{
    color: #ffffff;
    font-size: 16px;
    font-weight: 600;
}}
QToolButton#headerIconButton {{
    background: rgba(255, 255, 255, 0.16);
    border: none;
    border-radius: 8px;
    padding: 6px;
    color: #ffffff;
    font-size: 15px;
}}
QToolButton#headerIconButton:hover {{
    background: rgba(255, 255, 255, 0.30);
}}
QFrame#card {{
    border-radius: 10px;
    padding: 4px;
}}
QLabel#titleLabel {{
    font-size: 13px;
    font-weight: 600;
}}
QLabel#statusLabel {{
    font-size: 12px;
}}
QPushButton#fetchButton {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {ACCENT_FROM}, stop:1 {ACCENT_TO});
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
    font-weight: 600;
}}
QPushButton#fetchButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #8B4FF5, stop:1 #3B74F2);
}}
QPushButton#fetchButton:disabled {{
    background: #9aa0a6;
}}
QPushButton#videoButton {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {ACCENT_FROM}, stop:1 {ACCENT_TO});
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    font-weight: 600;
}}
QPushButton#videoButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #8B4FF5, stop:1 #3B74F2);
}}
QPushButton#audioButton {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {WARM_FROM}, stop:1 {WARM_TO});
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    font-weight: 600;
}}
QPushButton#audioButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #FF7784, stop:1 #FFCE8C);
}}
QPushButton#videoButton:disabled, QPushButton#audioButton:disabled {{
    background: #9aa0a6;
    color: #eeeeee;
}}
QPushButton#browseButton {{
    border-radius: 8px;
    padding: 6px 14px;
}}
QProgressBar {{
    border: none;
    border-radius: 8px;
    text-align: center;
    font-weight: 600;
    min-height: 22px;
}}
QProgressBar::chunk {{
    border-radius: 8px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {WARM_FROM}, stop:1 {WARM_TO});
}}
"""

LIGHT_STYLE = _SHARED + """
QWidget {
    background-color: #f5f6fa;
    color: #1f2430;
    font-size: 13px;
}
QFrame#headerBar QLabel {
    color: #ffffff;
}
QFrame#card {
    background-color: #ffffff;
    border: 1px solid #e3e5ec;
}
QLineEdit, QComboBox {
    background-color: #ffffff;
    border: 1px solid #d7d9e3;
    border-radius: 8px;
    padding: 7px;
    color: #1f2430;
}
QLineEdit:focus, QComboBox:focus {
    border: 1px solid #7C3AED;
}
QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #1f2430;
    selection-background-color: #ece6fd;
}
QPushButton#browseButton {
    background-color: #eceef4;
    border: 1px solid #d7d9e3;
    color: #1f2430;
}
QPushButton#browseButton:hover {
    background-color: #e1e4ee;
}
QProgressBar {
    background-color: #e9eaf2;
    color: #1f2430;
}
QLabel#statusLabel {
    color: #6b7280;
}
"""

DARK_STYLE = _SHARED + """
QWidget {
    background-color: #1c1e26;
    color: #e7e8ee;
    font-size: 13px;
}
QFrame#card {
    background-color: #262933;
    border: 1px solid #34384a;
}
QLineEdit, QComboBox {
    background-color: #2c303c;
    border: 1px solid #3d4152;
    border-radius: 8px;
    padding: 7px;
    color: #e7e8ee;
}
QLineEdit:focus, QComboBox:focus {
    border: 1px solid #8B5CF6;
}
QComboBox QAbstractItemView {
    background-color: #2c303c;
    color: #e7e8ee;
    selection-background-color: #3d4152;
}
QPushButton#browseButton {
    background-color: #2c303c;
    border: 1px solid #3d4152;
    color: #e7e8ee;
}
QPushButton#browseButton:hover {
    background-color: #363b4a;
}
QProgressBar {
    background-color: #2c303c;
    color: #e7e8ee;
}
QLabel#statusLabel {
    color: #9aa0b4;
}
"""


def stylesheet_for(dark_mode: bool) -> str:
    return DARK_STYLE if dark_mode else LIGHT_STYLE
