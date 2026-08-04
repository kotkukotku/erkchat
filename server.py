#server.py

import socket
import threading
import json

import database
import auth
import messages
import commands
from protocol import send_json

lock = threading.Lock()
database.init_db()

ip = "0.0.0.0"
port = 4444
clients = []
nicknames = {}
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((ip, port))
s.listen()


def get_nickname(conn):
    with lock:
        return nicknames.get(conn, "Unknown")
def broadcast(new_msg, sender_client):
    with lock:
        current_clients = clients.copy()
    for client in current_clients:
        if sender_client != client:
            try:
                send_json(client, new_msg)
            except:
                reseting(client)


def reseting(conn):
    with lock:
        try:
            clients.remove(conn)
        except Exception as e:
            print("Hata oluştu: ", e)
        nicknames.pop(conn, None)
    try:
        conn.close()
    except:
        pass


def receive(conn, addr):
    f = conn.makefile("r", encoding="utf-8", errors="ignore")
    current_nick, user_role = auth.handle_client_auth(
        conn,
        f,
        nicknames,
        lock,
        broadcast
    )

    if current_nick is None:
        reseting(conn)
        return

    old_messages = database.get_last_messages()
    if old_messages:
        send_json(conn, {
            "type":"system",
            "text":"--GEÇMİŞ MESAJLAR--\n"
        })
        for sender, message, receiver, time in old_messages:
            send_json(conn, {
                "type":"chat",
                "text":f"[{time}] {sender}: {message}"
            })
        send_json(conn, {
        "type": "system",
        "text": "-----------------------",
        })
    while True:
        raw = f.readline()
        if not raw:
            nickname = get_nickname(conn)
            reseting(conn)
            if nickname:
                broadcast({
                    "type": "system",
                    "text": f"{nickname} ayrıldı.",
                }, conn)
            break

        raw = raw.strip()
        if not raw:
            continue

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue

        if data.get("type") == "msg":
            messages.handle_message(
                conn,
                data["text"],
                nicknames,
                lock,
                broadcast
            )
            continue

        if data.get("type") == "exit":
            nickname = get_nickname(conn)
            broadcast({
                "type": "system",
                "text": f"{nickname} ayrıldı.",
            }, conn)
            shut_msg = {
                "type": "system",
                "event": "shutdown",
                "text": "Başarıyla çıkış yapıldı.",
            }
            send_json(conn, shut_msg)
            reseting(conn)
            break

        if data.get("type") == "command" and data.get("name") == "users":
            commands.handle_users(conn,nicknames,lock)
            continue

        if data.get("type") == "nick":
            commands.handle_nick(
                conn,
                data.get("new_name",""),
                nicknames,
                lock,
                broadcast)    
            continue
        if data.get("type") == "command" and data.get("name") == "help":
            commands.handle_help(conn)
            continue
        if data.get("type") == "command" and data.get("name") == "ping":
            send_json(conn,{
                "type": "ping_response",
                "time": data.get("time")
            })
            continue
        if data.get("type") == "command" and data.get("name") == "whoami":
            commands.handle_whoami(conn,nicknames,user_role)
            continue
        if data.get("type") == "dm":
            messages.handle_dm(
                conn,
                data.get("to"),
                data.get("text",""),
                nicknames,
                lock,
                get_nickname
            )
            continue


print(f"Server {port} portunda başlatıldı. Kapatmak için Ctrl+C yapın.")
try:
    while True:
        try:
            conn, addr = s.accept()
            with lock:
                clients.append(conn)
            threading.Thread(target=receive, args=(conn, addr), daemon=True).start()
        except OSError:
            break
except KeyboardInterrupt:
    print("\nCtrl+C algılandı. Server kapatılıyor.")
finally:
    print("Bağlantılar sonlandırılıyor...")
    with lock:
        current_clients = clients.copy()
    for client in current_clients:
        try:
            send_json(client, {
                "type": "system",
                "event": "shutdown",
                "text": "Server kapatıldı.",
            })
            reseting(client)
        except Exception as e:
            print("Hata oluştu:", e)
    s.close()
    print("Server güvenli şekilde kapatıldı.")
