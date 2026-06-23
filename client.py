import socket
import threading
import json

running = True

def send_json(sock, data):
    sock.sendall((json.dumps(data) + "\n").encode())


try:
    ip = input("Enter IP address:")
    port = 4444
    s = socket.socket()
    s.connect((ip, port))
except Exception as e:
    print("Connection error:", e)
    exit()


def listen():
    global running
    f = s.makefile("r", encoding="utf-8", errors="ignore")

    for line in f:
        line = line.strip()
        if not line:
            continue

        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            print(line)
            continue

        if data.get("type") == "system":
            print(data.get("text"))
            if data.get("event") == "shutdown":
                running = False
                return
        elif data.get("type") == "dm":
            print(data.get("text"))
        elif data.get("type") == "chat":
            print(data.get("text"))

    print("Sunucuyla bağlantı koptu.")


threading.Thread(target=listen, daemon=True).start()
nickname = input("Kullanıcı adı girin: ")
s.sendall((nickname + "\n").encode())

while running:
    msg = input()

    if msg == "exit":
        data = {
            "type": "exit",
        }
        send_json(s, data)
        break
    elif msg == "/users":
        data = {
            "type": "command",
            "name": "users",
        }
    elif msg.startswith("/nick "):
        parts = msg.split(" ", 1)
        if len(parts) < 2:
            print("Kullanım: /nick (Yeni Kullanıcı Adı)")
            continue
        data = {
            "type": "nick",
            "new_name": parts[1],
        }

    elif msg.startswith("/msg "):
        parts = msg.split(" ", 2)
        if len(parts) < 3:
            print("Kullanım: /msg (Kullanıcı Adı) (Mesaj)")
            continue
        to = parts[1]
        text = parts[2]
        data = {
            "type": "dm",
            "to": to,
            "text": text,
        }
    elif msg == "/help":
        data = {
            "type": "command",
            "name": "help",
        }
        send_json(s, data)
        continue
    else:
        data = {
            "type": "msg",
            "text": msg,
        }
    send_json(s, data)

s.close()
