"""One-off dev script: renders the app icon at multiple sizes using QPainter.

Run with: python scripts/generate_icon.py
"""
import os
import sys

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QLinearGradient, QPainter, QPainterPath, QPixmap, QPolygonF
from PySide6.QtWidgets import QApplication

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "app", "resources")
SIZES = [16, 32, 48, 64, 128, 256, 512]

BG_TOP = QColor("#7C3AED")     # violet
BG_BOTTOM = QColor("#2563EB")  # blue
BADGE_TOP = QColor("#FF5F6D")  # coral
BADGE_BOTTOM = QColor("#FFC371")  # amber


def draw_icon(size: int) -> QPixmap:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Rounded-square gradient background
    margin = size * 0.04
    rect = QRectF(margin, margin, size - 2 * margin, size - 2 * margin)
    radius = size * 0.22
    path = QPainterPath()
    path.addRoundedRect(rect, radius, radius)

    gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
    gradient.setColorAt(0.0, BG_TOP)
    gradient.setColorAt(1.0, BG_BOTTOM)
    painter.fillPath(path, QBrush(gradient))

    # White play triangle, slightly left-of-center
    tri_size = size * 0.34
    cx, cy = size * 0.46, size * 0.44
    triangle = QPolygonF(
        [
            QPointF(cx - tri_size * 0.45, cy - tri_size * 0.55),
            QPointF(cx - tri_size * 0.45, cy + tri_size * 0.55),
            QPointF(cx + tri_size * 0.62, cy),
        ]
    )
    painter.setBrush(QBrush(QColor("#FFFFFF")))
    painter.setPen(Qt.NoPen)
    painter.drawPolygon(triangle)

    # Download badge (circle + arrow) bottom-right
    badge_r = size * 0.29
    badge_cx = size * 0.76
    badge_cy = size * 0.76
    badge_rect = QRectF(badge_cx - badge_r, badge_cy - badge_r, badge_r * 2, badge_r * 2)

    badge_gradient = QLinearGradient(badge_rect.topLeft(), badge_rect.bottomRight())
    badge_gradient.setColorAt(0.0, BADGE_TOP)
    badge_gradient.setColorAt(1.0, BADGE_BOTTOM)

    # subtle white ring so badge separates from background
    ring_rect = badge_rect.adjusted(-size * 0.02, -size * 0.02, size * 0.02, size * 0.02)
    painter.setBrush(QBrush(QColor("#FFFFFF")))
    painter.drawEllipse(ring_rect)

    painter.setBrush(QBrush(badge_gradient))
    painter.drawEllipse(badge_rect)

    # Down arrow inside badge
    arrow_w = badge_r * 0.7
    arrow_stem_w = badge_r * 0.26
    ax, ay = badge_cx, badge_cy
    stem = QRectF(ax - arrow_stem_w / 2, ay - badge_r * 0.42, arrow_stem_w, badge_r * 0.62)
    painter.setBrush(QBrush(QColor("#FFFFFF")))
    painter.drawRoundedRect(stem, arrow_stem_w * 0.3, arrow_stem_w * 0.3)

    head = QPolygonF(
        [
            QPointF(ax - arrow_w / 2, ay + badge_r * 0.12),
            QPointF(ax + arrow_w / 2, ay + badge_r * 0.12),
            QPointF(ax, ay + badge_r * 0.58),
        ]
    )
    painter.drawPolygon(head)

    painter.end()
    return pixmap


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    app = QApplication(sys.argv)  # QPixmap/QPainter need a QApplication instance
    for size in SIZES:
        pixmap = draw_icon(size)
        path = os.path.join(OUT_DIR, f"icon-{size}.png")
        pixmap.save(path, "PNG")
        print(f"wrote {path}")

    # Primary icon used by the app at runtime
    draw_icon(256).save(os.path.join(OUT_DIR, "icon.png"), "PNG")
    print("wrote icon.png (256px)")


if __name__ == "__main__":
    main()
