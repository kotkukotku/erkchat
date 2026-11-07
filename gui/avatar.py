
import hashlib

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget


class AvatarWidget(QWidget):

    def __init__(self, username, size=40, parent=None):
        super().__init__(parent)

        self.username = username.strip() or "?"
        self.setFixedSize(size, size)

        self.initials = self.create_initials()
        self.avatar_color = self.create_color()

        self.setToolTip(self.username)

    def create_initials(self):
        name = (
            self.username
            .replace("_", " ")
            .replace("-", " ")
        )

        parts = name.split()

        if len(parts) >= 2:
            return "".join(part[0] for part in parts[:2]).upper()

        return parts[0][0].upper() if parts else "?"

    def create_color(self):
        normalized = self.username.casefold()

        digest = hashlib.sha256(
            normalized.encode("utf-8")
        ).digest()

        hue = int.from_bytes(digest[:2], "big") % 360
        saturation = 165 + digest[2] % 60
        brightness = 175 + digest[3] % 45

        return QColor.fromHsv(
            hue,
            saturation,
            brightness
        )

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.avatar_color)

        painter.drawEllipse(
            self.rect().adjusted(1, 1, -1, -1)
        )

        font = painter.font()
        font.setBold(True)
        font.setPointSize(
            max(8, round(self.width() * 0.34))
        )

        painter.setFont(font)
        painter.setPen(Qt.GlobalColor.white)

        painter.drawText(
            self.rect(),
            Qt.AlignmentFlag.AlignCenter,
            self.initials
        )

        painter.end()
