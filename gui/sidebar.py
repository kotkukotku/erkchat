
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QListWidget,
    QVBoxLayout,
)


class Sidebar(QFrame):

    # Kullanıcı bir oda seçtiğinde oda adını dışarıya bildirir.
    room_changed = Signal(str)

    def __init__(self):
        super().__init__()

        self.setObjectName("sidebar")
        self.setFixedWidth(220)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 20, 15, 15)

        title = QLabel("ErkChat")
        title.setObjectName("app_title")

        rooms_label = QLabel("SOHBET ODALARI")
        rooms_label.setObjectName("section_title")

        self.room_list = QListWidget()
        self.room_list.addItems([
            "genel",
            "teknoloji",
            "yazılım",
            "linux",
            "güvenlik",
        ])

        self.room_list.setCurrentRow(0)

        self.room_list.currentTextChanged.connect(
            self.room_changed.emit
        )

        layout.addWidget(title)
        layout.addSpacing(30)
        layout.addWidget(rooms_label)
        layout.addWidget(self.room_list)
        layout.addStretch()

        profile = QLabel("●  Erkam\n    Çevrimiçi")
        profile.setStyleSheet(
            "background-color: #292a30; padding: 12px; "
            "border-radius: 8px;"
        )

        layout.addWidget(profile)
    def set_current_room(self, room_name):
        items = self.room_list.findItems(
            room_name,
            Qt.MatchFlag.MatchExactly
        )

        if not items:
            return

        previous_state = self.room_list.blockSignals(True)

        self.room_list.setCurrentItem(items[0])

        self.room_list.blockSignals(previous_state)
