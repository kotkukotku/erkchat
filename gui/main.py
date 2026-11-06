
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

message_history = {
    "genel": [],
    "teknoloji": [],
    "yazılım": [],
    "linux": [],
    "güvenlik": []
}

class ErkChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.message_history = {}
        self.current_room = "genel"
        self.setWindowTitle("ErkChat")
        self.resize(1200, 750)
        self.setMinimumSize(850, 550)

        self.setup_style()
        self.setup_ui()

    def setup_style(self):
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1e1f22;
                color: #eeeeF2;
                font-family: Sans Serif;
                font-size: 14px;
            }

            QFrame#sidebar {
                background-color: #17181c;
            }

            QFrame#members {
                background-color: #232429;
            }

            QLabel#app_title {
                color: #b49aff;
                font-size: 22px;
                font-weight: bold;
            }

            QLabel#section_title {
                color: #92949c;
                font-size: 11px;
                font-weight: bold;
            }

            QLabel#channel_title {
                font-size: 19px;
                font-weight: bold;
            }

            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
            }

            QListWidget::item {
                padding: 11px;
                border-radius: 6px;
            }

            QListWidget::item:selected {
                background-color: #49405f;
            }

            QLineEdit {
                background-color: #383a40;
                border: none;
                border-radius: 9px;
                padding: 13px;
                color: white;
            }

            QPushButton {
                background-color: #7955db;
                border: none;
                border-radius: 8px;
                padding: 11px 18px;
                color: white;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #916ff0;
            }
        """)

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.create_sidebar(main_layout)
        self.create_chat_panel(main_layout)
        self.create_members_panel(main_layout)

    def create_sidebar(self, main_layout):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)

        layout = QVBoxLayout(sidebar)
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
            self.change_room
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

        main_layout.addWidget(sidebar)

    def create_chat_panel(self, main_layout):
        chat_panel = QWidget()
        layout = QVBoxLayout(chat_panel)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(12)

        self.channel_title = QLabel("# genel")
        self.channel_title.setObjectName("channel_title")

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("color: #383940;")

        self.message_area = QVBoxLayout()
        self.message_area.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        message_container = QWidget()
        message_container.setLayout(self.message_area)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(message_container)
        scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
        )

        welcome = QLabel(
            "ErkChat'e hoş geldin!\n"
            "Sohbet ekranımızı birlikte geliştiriyoruz."
        )
        welcome.setStyleSheet(
            "background-color: #292a30; padding: 15px; "
            "border-radius: 9px;"
        )
        welcome.setWordWrap(True)

        self.message_area.addWidget(welcome)

        input_layout = QHBoxLayout()

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText(
            "Mesajını yaz..."
        )
        self.message_input.returnPressed.connect(
            self.send_message
        )

        send_button = QPushButton("Gönder")
        send_button.clicked.connect(self.send_message)

        input_layout.addWidget(self.message_input, 1)
        input_layout.addWidget(send_button)

        layout.addWidget(self.channel_title)
        layout.addWidget(separator)
        layout.addWidget(scroll, 1)
        layout.addLayout(input_layout)

        main_layout.addWidget(chat_panel, 1)

    def create_members_panel(self, main_layout):
        members = QFrame()
        members.setObjectName("members")
        members.setFixedWidth(190)

        layout = QVBoxLayout(members)
        layout.setContentsMargins(15, 20, 15, 15)

        title = QLabel("ÇEVRİMİÇİ")
        title.setObjectName("section_title")

        self.member_list = QListWidget()
        self.member_list.addItems([
            "● Erkam",
            "● Kullanıcı 2",
            "● Kullanıcı 3",
        ])

        layout.addWidget(title)
        layout.addWidget(self.member_list)
        layout.addStretch()

        main_layout.addWidget(members)

    def change_room(self, room_name):
        if not room_name:
            return

        self.current_room = room_name
        self.channel_title.setText(f"# {room_name}")

        self.update_messages()
    def update_messages(self):
        while self.message_area.count():
            item = self.message_area.takeAt(0)

            widget = item.widget()
            if widget:
                widget.deleteLater()

        history = self.message_history.get(
            self.current_room, []
        )

        for text in history:
            message = QLabel(text)
            message.setWordWrap(True)
            message.setStyleSheet("""
                background-color: #292a30;
                padding: 12px;
                border-radius: 8px;
            """)

            self.message_area.addWidget(message)
    def send_message(self):
        text = self.message_input.text().strip()

        if not text:
            return

        message_text = f"Erkam\n\n{text}"

        self.message_history.setdefault(
            self.current_room, []
        ).append(message_text)

        self.update_messages()
        self.message_input.clear()


def main():
    app = QApplication(sys.argv)

    window = ErkChatWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
