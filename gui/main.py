
import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QInputDialog,
    QMessageBox,
)
from styles import MAIN_STYLE
from sidebar import Sidebar
from chat import ChatPanel
from members import MembersPanel
from network import NetworkClient
from auth_dialog import AuthDialog
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

        self.network = None
        self.authenticated = False
        self.auth_dialog = None
        self.pending_auth_action = None
        self.pending_room = None
        self.pending_username = None

        self.room_change_timer = QTimer(self)
        self.room_change_timer.setSingleShot(True)
        self.room_change_timer.timeout.connect(
            self.on_room_change_timeout
        )

        self.setWindowTitle("ErkChat")
        self.resize(1200, 750)
        self.setMinimumSize(850, 550)

        self.setStyleSheet(MAIN_STYLE)
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

        self.sidebar = Sidebar()
        self.sidebar.room_changed.connect(self.change_room)
        main_layout.addWidget(self.sidebar)

        self.chat_panel = ChatPanel()
        self.chat_panel.message_sent.connect(self.send_message)
        main_layout.addWidget(self.chat_panel, 1)

        self.members_panel = MembersPanel()
        main_layout.addWidget(self.members_panel)
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

        profile = QLabel(f"●  Erkam\n    Çevrimiçi")
        profile.setStyleSheet(
            "background-color: #292a30; padding: 12px; "
            "border-radius: 8px;"
        )

        layout.addWidget(profile)

        main_layout.addWidget(sidebar)

    
    
    
    def change_room(self, room_name):
        if not room_name:
            return

        if not self.authenticated:
            self.current_room = room_name
            self.chat_panel.set_room(room_name)
            return

        if room_name == self.current_room:
            return

        if room_name == self.pending_room:
            return

        self.pending_room = room_name

        self.statusBar().showMessage(
            f"#{room_name} odasına geçiliyor..."
        )

        self.room_change_timer.start(5000)

        success = self.network.send_command(
            "join",
            room=room_name
        )

        if not success:
            self.room_change_timer.stop()
            self.pending_room = None

            self.sidebar.set_current_room(
                self.current_room
            )

            self.statusBar().showMessage(
                "Oda değiştirme isteği gönderilemedi.",
                3000
            )


    def create_message(self, username, text):
        message_box = QFrame()
        message_box.setStyleSheet("""
            QFrame {
                background-color: #292a30;
                border-radius: 9px;
            }
        """)

        layout = QVBoxLayout(message_box)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(5)

        username_label = QLabel(username)
        username_label.setStyleSheet("""
            color: #b49aff;
            font-size: 16px;
            font-weight: bold;
            background: transparent;
        """)

        message_label = QLabel(text)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("""
            color: #eeeeF2;
            font-size: 14px;
            background: transparent;
        """)

        layout.addWidget(username_label)
        layout.addWidget(message_label)

        return message_box


    
    def update_messages(self):
        self.chat_panel.clear_messages()

        history = self.message_history.get(
            self.current_room, []
        )

        for entry in history:
            if len(entry) == 3:
                username, text, timestamp = entry
            else:
                username, text = entry
                timestamp = None

            self.chat_panel.add_message(
                username,
                text,
                timestamp
            )

    def send_message(self, text):
        if not self.authenticated or not self.network:
            return

        self.network.send_message(text)
    def connect_to_server(self, host):
        self.network = NetworkClient(host, 4444)

        self.network.connected.connect(self.on_connected)
        self.network.disconnected.connect(self.on_disconnected)
        self.network.message_received.connect(
            self.handle_server_message
        )
        self.network.error_occurred.connect(
            self.on_network_error
        )

        self.network.start()

    def on_connected(self):
        self.auth_dialog = AuthDialog(self)

        self.auth_dialog.auth_requested.connect(
            self.authenticate_user
        )

        self.auth_dialog.rejected.connect(
            self.cancel_authentication
        )

        self.auth_dialog.show()
    def authenticate_user(self, action, username, password):
        self.pending_auth_action = action
        self.pending_username = username
        success = self.network.authenticate(
            action,
            username,
            password
        )

        if not success:
            self.auth_dialog.set_status(
                "Sunucuya istek gönderilemedi.",
                False
            )
            
    def cancel_authentication(self):
        if self.network and self.network.isRunning():
            self.network.disconnect_from_server()

    
    
    def handle_server_message(self, data):
        msg_type = data.get("type")

        # KİMLİK DOĞRULAMA
        if msg_type == "auth_response":
            success = data.get("success", False)
            message = data.get("message", "")

            if not success:
                if self.auth_dialog:
                    self.auth_dialog.set_status(message, False)
                return

            # Kayıt başarılıysa giriş penceresini açık tut.
            if self.pending_auth_action == "register":
                self.auth_dialog.set_status(message, True)
                return

            # Giriş başarılı.
            self.authenticated = True
            self.sidebar.set_username(self.pending_username)

            self.auth_dialog.accept()
            self.auth_dialog = None

            self.pending_room = self.current_room

            self.network.send_command(
                "join",
                room=self.current_room
            )

            return
        # ÇEVRİMİÇİ KULLANICILAR
        if msg_type == "users":
            room_name = data.get("room")
            users = data.get("users", [])

            if room_name == self.current_room:
                self.members_panel.set_members(users)

            return
        # NORMAL SOHBET MESAJI
        
        if msg_type == "chat":
            room_name = data.get("room", self.current_room)
            username = data.get("username", "Bilinmeyen")
            text = data.get("text", "")
            timestamp = data.get("timestamp")

            self.message_history.setdefault(
                room_name, []
            ).append((username, text, timestamp))

            if room_name == self.current_room:
                self.chat_panel.add_message(
                    username,
                    text,
                    timestamp
                )

            return

        # ÖZEL MESAJ
        if msg_type == "dm":
            username = data.get("username", "DM")
            text = data.get("text", "")
            timestamp = data.get("timestamp")

            self.chat_panel.add_message(
                username,
                text,
                timestamp
            )

            return
        # SİSTEM OLAYLARI
        if msg_type == "system":
            event = data.get("event")

            # Başka kullanıcıların odaya girmesi veya çıkması.
            # Bunları sohbet akışına eklemiyoruz.
            if event in ("member_joined", "member_left"):

                room_name = data.get("room")

                if room_name == self.current_room:
                    self.network.send_command("users")

                return

            # Sunucu oda değiştirmeyi onayladı.
            if event == "room_changed":
                room_name = data.get("room")

                if not room_name:
                    return

                self.room_change_timer.stop()

                self.current_room = room_name
                self.pending_room = None

                self.chat_panel.set_room(room_name)

                self.message_history[room_name] = []
                self.update_messages()

                self.sidebar.set_current_room(room_name)

                self.statusBar().clearMessage()

                self.statusBar().showMessage(
                    f"#{room_name} odasına geçildi.",
                    2500
                )

                # Yeni odanın gerçek üyelerini iste.
                self.network.send_command("users")

                return

            # Oda değiştirilemedi.
            if event == "room_change_failed":
                self.room_change_timer.stop()
                self.pending_room = None

                self.sidebar.set_current_room(
                    self.current_room
                )

                self.statusBar().showMessage(
                    data.get("text", "Oda değiştirilemedi."),
                    3500
                )

                return

            # Diğer sistem yanıtları.
            text = data.get("text", "").strip()

            if not text:
                return

            if len(text) <= 90 and "\n" not in text:
                self.statusBar().showMessage(text, 3500)
            else:
                self.chat_panel.add_system_message(text)


    def on_network_error(self, error):
        QMessageBox.critical(
            self,
            "Bağlantı hatası",
            f"Sunucuya bağlanılamadı:\n{error}"
        )

    def on_disconnected(self):
        self.authenticated = False

    def closeEvent(self, event):
        if self.network and self.network.isRunning():
            self.network.disconnect_from_server()
            self.network.wait(1500)

        event.accept()
    def on_room_change_timeout(self):
        if self.pending_room is None:
            return

        failed_room = self.pending_room
        self.pending_room = None

        self.sidebar.set_current_room(
            self.current_room
        )

        self.statusBar().showMessage(
            f"#{failed_room} için sunucudan yanıt alınamadı.",
            5000
        )

def main():
    app = QApplication(sys.argv)

    host, ok = QInputDialog.getText(
        None,
        "ErkChat",
        "Sunucu IP adresi:"
    )

    if not ok or not host.strip():
        return

    window = ErkChatWindow()
    window.show()

    window.connect_to_server(host.strip())

    sys.exit(app.exec())


if __name__ == "__main__":
    main()