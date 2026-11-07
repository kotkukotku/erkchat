
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
)


class AuthDialog(QDialog):

    auth_requested = Signal(str, str, str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("ErkChat | Hesap")
        self.setFixedWidth(360)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(12)

        title = QLabel("ErkChat'e Hoş Geldin")
        title.setObjectName("app_title")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Kullanıcı adı")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Şifre")
        self.password_input.setEchoMode(
            QLineEdit.EchoMode.Password
        )

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)

        buttons = QHBoxLayout()

        login_button = QPushButton("Giriş Yap")
        register_button = QPushButton("Kayıt Ol")

        login_button.clicked.connect(
            lambda: self.submit("login")
        )

        register_button.clicked.connect(
            lambda: self.submit("register")
        )

        buttons.addWidget(login_button)
        buttons.addWidget(register_button)

        layout.addWidget(title)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.status_label)
        layout.addLayout(buttons)

    def submit(self, action):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            self.set_status(
                "Kullanıcı adı ve şifre boş olamaz.",
                False
            )
            return

        self.auth_requested.emit(
            action,
            username,
            password
        )

    def set_status(self, message, success=False):
        color = "#75d69c" if success else "#ff7777"

        self.status_label.setStyleSheet(
            f"color: {color};"
        )

        self.status_label.setText(message)
