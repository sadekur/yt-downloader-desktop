"""Light/dark stylesheets for the app."""

LIGHT_STYLE = ""  # default Qt platform style

DARK_STYLE = """
QWidget {
    background-color: #2b2b2b;
    color: #e0e0e0;
    font-size: 13px;
}
QLineEdit, QComboBox {
    background-color: #3c3c3c;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 4px;
    color: #e0e0e0;
}
QComboBox QAbstractItemView {
    background-color: #3c3c3c;
    color: #e0e0e0;
    selection-background-color: #505050;
}
QPushButton {
    background-color: #454545;
    border: 1px solid #5a5a5a;
    border-radius: 4px;
    padding: 6px 12px;
}
QPushButton:hover {
    background-color: #525252;
}
QPushButton:disabled {
    color: #888;
    background-color: #3a3a3a;
}
QProgressBar {
    border: 1px solid #555;
    border-radius: 4px;
    text-align: center;
    background-color: #3c3c3c;
}
QProgressBar::chunk {
    background-color: #3daee9;
    border-radius: 4px;
}
QLabel#statusLabel {
    color: #aaaaaa;
}
QCheckBox {
    spacing: 6px;
}
"""


def stylesheet_for(dark_mode: bool) -> str:
    return DARK_STYLE if dark_mode else LIGHT_STYLE
