from avatar import AvatarWidget
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)


class ChatPanel(QWidget):

    # Ana pencereye mesaj gönderme sinyali.
    message_sent = Signal(str)

    def __init__(self):
        super().__init__()

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(12)

        # Oda başlığı
        self.channel_title = QLabel("# genel")
        self.channel_title.setObjectName("channel_title")

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("color: #383940;")

        # Mesajların yerleştirileceği alan
        self.message_area = QVBoxLayout()
        self.message_area.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        message_container = QWidget()
        message_container.setLayout(self.message_area)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(message_container)
        self.scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
        )

        # Mesaj yazma alanı
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
        layout.addWidget(self.scroll, 1)
        layout.addLayout(input_layout)

    def set_room(self, room_name):
        self.channel_title.setText(f"# {room_name}")

    def send_message(self):
        text = self.message_input.text().strip()

        if not text:
            return

        self.message_sent.emit(text)
        self.message_input.clear()

    
    def add_message(self, username, text, timestamp=None):
        message_box = QFrame()

        message_box.setStyleSheet("""
            QFrame {
                background-color: #292a30;
                border-radius: 9px;
            }
        """)

        row_layout = QHBoxLayout(message_box)
        row_layout.setContentsMargins(12, 10, 12, 10)
        row_layout.setSpacing(12)

        # Kullanıcı avatarı
        avatar = AvatarWidget(username, size=40)

        # Mesaj içeriği
        content = QWidget()
        message_layout = QVBoxLayout(content)

        message_layout.setContentsMargins(0, 0, 0, 0)
        message_layout.setSpacing(5)

        # Kullanıcı adı ve saat
        header_layout = QHBoxLayout()
        header_layout.setSpacing(9)

        username_label = QLabel(username)
        username_label.setStyleSheet("""
            color: #b49aff;
            font-size: 15px;
            font-weight: bold;
            background: transparent;
        """)

        header_layout.addWidget(username_label)

        if timestamp:
            timestamp_label = QLabel(timestamp)

            timestamp_label.setStyleSheet("""
                color: #92949c;
                font-size: 11px;
                background: transparent;
            """)

            header_layout.addWidget(timestamp_label)

        header_layout.addStretch()

        # Mesaj metni
        message_label = QLabel(text)
        message_label.setWordWrap(True)

        message_label.setStyleSheet("""
            color: #eeeeF2;
            font-size: 14px;
            background: transparent;
        """)

        message_layout.addLayout(header_layout)
        message_layout.addWidget(message_label)

        row_layout.addWidget(
            avatar,
            0,
            Qt.AlignmentFlag.AlignTop
        )

        row_layout.addWidget(content, 1)

        self.message_area.addWidget(message_box)

        self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()
        )


    def clear_messages(self):
        while self.message_area.count():
            item = self.message_area.takeAt(0)

            widget = item.widget()
            if widget:
                widget.deleteLater()

    def add_system_message(self, text):
        label = QLabel(text.strip())
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label.setStyleSheet("""
            QLabel {
                color: #92949c;
                font-size: 12px;
                padding: 5px;
                background: transparent;
            }
        """)

        self.message_area.addWidget(label)
