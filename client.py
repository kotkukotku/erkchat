#client.py

import socket
import threading
import json
from colorama import Fore, init, Style
import os
import time
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


def listen(f):
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
        elif data.get("type") == "ping_response":
            start = time.perf_counter()
            latency = (start - data.get("time")) * 1000
            print(Fore.CYAN + f"Gecikme: {latency:.2f} ms\n")


    print("Sunucuyla bağlantı koptu.")
    running.clear()
    os._exit(0)
authenticated = False

f = s.makefile("r", encoding="utf-8", errors="ignore")
while not authenticated:
    print("""
1 - Giriş yap
2 - Kayıt ol
""")

    choice = input("Seçim: ").strip()



    if choice not in ["1","2"]:
        print(Fore.RED + "Geçersiz seçim. Lütfen tekrar deneyin")
        continue
    username = input("Kullanıcı adı: ").strip()
    password = input("Şifre: ").strip()
    if not username or not password:
        print(Fore.RED + "Kullanıcı adı veya şifre boş bırakılamaz.")
        continue
    if choice == "1":
        action = "login"
    if choice == "2":
        action = "register"

    send_json(s, {
        "type": "auth",
        "action": action,
        "username": username,
        "password": password
    })

    response_line = f.readline()
    if not response_line:
        print(Fore.RED + "Sunucuyla bağlantı kesildi.")
        os._exit(0)
    
    try:
        response = json.loads(response_line.strip())
    except json.JSONDecodeError:
        print(Fore.RED + "Sunucudan anlaşılmayan yanıt alındı.")
        continue
    
    if response.get("type") == "auth_response":
        success = response.get("success", False)
        message = response.get("message","")
        if success:
            print(Fore.GREEN + message)
            if action == "login":
                authenticated = True
        else:
            print(Fore.RED + message)

threading.Thread(target=listen, args=(f,),daemon=True).start()


while running.is_set():
    try:
        msg = input().strip()
    except KeyboardInterrupt:
        break

    if not msg:
        continue
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
    elif msg == "/ping":
        data = {
            "type":"command",
            "name":"ping",
            "time": time.perf_counter()
        }
        send_json(s,data)
        continue
    elif msg == "/whoami":
        data = {
        "type": "command",
        "name": "whoami",
        }
        send_json(s,data)
        continue
    else:
        data = {
            "type": "msg",
            "text": msg,
        }
    send_json(s, data)

s.close()