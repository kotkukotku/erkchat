
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
)

from avatar import AvatarWidget


class MembersPanel(QFrame):

    def __init__(self):
        super().__init__()

        self.setObjectName("members")
        self.setFixedWidth(190)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        layout.setContentsMargins(15, 20, 15, 15)
        layout.setSpacing(12)

        self.title = QLabel("ÇEVRİMİÇİ · 0")
        self.title.setObjectName("section_title")

        self.member_list = QListWidget()
        self.member_list.setSpacing(3)

        layout.addWidget(self.title)
        layout.addWidget(self.member_list)
        layout.addStretch()

    def set_members(self, members):
        self.member_list.clear()

        self.title.setText(
            f"ÇEVRİMİÇİ · {len(members)}"
        )

        if not members:
            self.member_list.addItem(
                "Çevrimiçi kullanıcı yok"
            )
            return

        for username in members:
            row = QWidget()
            row_layout = QHBoxLayout(row)

            row_layout.setContentsMargins(5, 4, 5, 4)
            row_layout.setSpacing(9)

            avatar = AvatarWidget(
                username,
                size=29
            )

            name_label = QLabel(username)

            name_label.setStyleSheet("""
                color: #eeeeF2;
                font-size: 13px;
                background: transparent;
            """)

            row_layout.addWidget(avatar)
            row_layout.addWidget(name_label, 1)

            item = QListWidgetItem()
            item.setSizeHint(row.sizeHint())

            self.member_list.addItem(item)
            self.member_list.setItemWidget(item, row)
