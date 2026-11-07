
import json
import socket
import queue

from PySide6.QtCore import QThread, Signal


class NetworkClient(QThread):

    connected = Signal()
    disconnected = Signal()
    message_received = Signal(dict)
    error_occurred = Signal(str)

    def __init__(self, host, port=4444):
        super().__init__()

        self.host = host
        self.port = port

        self.outgoing = queue.Queue()
        self.running = False

    def run(self):
        sock = None
        buffer = b""

        try:
            sock = socket.create_connection(
                (self.host, self.port),
                timeout=5
            )

            sock.settimeout(0.2)
            self.running = True

            self.connected.emit()

            while self.running:

                # Gönderilecek verileri kontrol et
                try:
                    while True:
                        data = self.outgoing.get_nowait()

                        if data is None:
                            self.running = False
                            break

                        raw = (
                            json.dumps(data, ensure_ascii=False) + "\n"
                        ).encode("utf-8")

                        sock.sendall(raw)

                except queue.Empty:
                    pass

                if not self.running:
                    break

                # Sunucudan veri oku
                try:
                    chunk = sock.recv(4096)

                    if not chunk:
                        break

                    buffer += chunk

                except socket.timeout:
                    continue

                # Tamamlanmış JSON satırlarını işle
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)

                    if not line.strip():
                        continue

                    try:
                        data = json.loads(line.decode("utf-8"))
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        continue

                    self.message_received.emit(data)

                    if (
                        data.get("type") == "system"
                        and data.get("event") == "shutdown"
                    ):
                        self.running = False
                        break

        except OSError as e:
            self.error_occurred.emit(str(e))

        finally:
            self.running = False

            if sock is not None:
                try:
                    sock.close()
                except OSError:
                    pass

            self.disconnected.emit()

    def send_data(self, data):
        if not self.isRunning() or not self.running:
            return False

        self.outgoing.put(data)
        return True

    def authenticate(self, action, username, password):
        return self.send_data({
            "type": "auth",
            "action": action,
            "username": username,
            "password": password
        })

    def send_message(self, text):
        return self.send_data({
            "type": "msg",
            "text": text
        })

    def send_command(self, name, **kwargs):
        return self.send_data({
            "type": "command",
            "name": name,
            **kwargs
        })

    def disconnect_from_server(self):
        if self.isRunning() and self.running:
            self.send_data({"type": "exit"})
            self.outgoing.put(None)
