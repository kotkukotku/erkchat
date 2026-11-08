
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QListWidget,
    QVBoxLayout,
    QHBoxLayout,
)
from avatar import AvatarWidget

class Sidebar(QFrame):

    # Kullanıcı bir oda seçtiğinde oda adını dışarıya bildirir.
    room_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self.profile = QFrame()
        self.setObjectName("sidebar")
        self.setFixedWidth(220)
        self.username_label = QLabel("Erkam")
        self.status_label = QLabel("● Çevrimiçi")
        self.avatar = AvatarWidget("?", size=40)
        
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 20, 15, 15)

        

        profile_layout = QVBoxLayout(self.profile)
        self.profile_content = QHBoxLayout()
        user_info_layout = QVBoxLayout()

        user_info_layout.addWidget(self.username_label)
        user_info_layout.addWidget(self.status_label)

        self.profile_content.addWidget(self.avatar)
        self.profile_content.addLayout(user_info_layout)

        profile_layout.addLayout(self.profile_content)

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


        self.profile.setStyleSheet(
            "background-color: #292a30; padding: 12px; "
            "border-radius: 8px;"
        )

        layout.addWidget(self.profile)
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
    def set_username(self, username):
        self.username_label.setText(username)

        new_avatar = AvatarWidget(username, size=40)

        self.profile_content.replaceWidget(
            self.avatar,
            new_avatar
        )

        self.avatar.deleteLater()
        self.avatar = new_avatar