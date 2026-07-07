#client.py

import socket
import threading
import json
from colorama import Fore, init, Style
import os
init(autoreset=True)

running = threading.Event()
running.set()

def send_json(sock, data):
    try:
        sock.sendall((json.dumps(data) + "\n").encode())
    except:
        pass


try:
    ip = input("Enter IP address:")
    port = 4444
    s = socket.socket()
    s.connect((ip, port))
except Exception as e:
    print(Fore.RED + "Connection error:", e)
    exit()


def listen():
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
            print(Fore.YELLOW + data.get("text"))
            if data.get("event") == "shutdown":
                running.clear()
                os._exit(0)
                return
        elif data.get("type") == "dm":
            print(Fore.MAGENTA + data.get("text"))
        elif data.get("type") == "chat":
            print(Fore.GREEN + data.get("text"))

    print("Sunucuyla bağlantı koptu.")
    running.clear()
    os._exit(0)

threading.Thread(target=listen, daemon=True).start()
nickname = input("Kullanıcı adı girin: ")
s.sendall((nickname + "\n").encode())

while running.is_set():
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
            print("Kullanım: /nick (Yeni Kullanıcı Adı)\n")
            continue
        data = {
            "type": "nick",
            "new_name": parts[1],
        }

    elif msg.startswith("/msg "):
        parts = msg.split(" ", 2)
        if len(parts) < 3:
            print("Kullanım: /msg (Kullanıcı Adı) (Mesaj)\n")
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
