#server.py

import socket
import threading
import collections
import json
from datetime import datetime 

lock = threading.Lock()

ip = "0.0.0.0"
port = 4444
clients = []
nicknames = {}
message_log = collections.deque(maxlen=10)
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((ip, port))
s.listen()


def send_json(conn, data):
    conn.sendall((json.dumps(data) + "\n").encode())

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

    try:
        nickname = f.readline().strip()
        if not nickname:
            raise Exception("Kullanıcı adı belirtilmedi.")
        with lock:
            name_exists = nickname in nicknames.values()
            if not name_exists:
                nicknames[conn] = nickname
                current_nick = nickname
        if name_exists:
            send_json(conn,{
                "type":"system",
                "event":"shutdown",
                "text":"Bu kullanıcı adı zaten var."
            })
            reseting(conn)
            return
        print(current_nick, "bağlandı.")

        broadcast({
            "type": "system",
            "text": f"{current_nick} bağlandı.",
        }, conn)
    except:
        reseting(conn)
        return

    if message_log:
        send_json(conn, {
            "type": "system",
            "text": "--GEÇMİŞ MESAJLAR--\n",
        })
        with lock:
            logs = list(message_log)
        for old_msg in logs:
            send_json(conn, old_msg)
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
            text = data["text"]
            with lock:
                sender = nicknames[conn]
            current_time = datetime.now().strftime("%H:%M")
            new_msg = {
                "type": "chat",
                "text": f"[{current_time}] {sender}: {text}",
            }
            with lock:
                message_log.append(new_msg)
            broadcast(new_msg, conn)
            send_json(conn,new_msg)
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
            with lock:
                user_list = "\n".join(nicknames.values())
            users_msg = {
                "type": "system",
                "text": f"Online users:\n{user_list}\n",
            }
            send_json(conn, users_msg)
            continue

        if data.get("type") == "nick":
            old_nickname = nicknames.get(conn)
            new_user = data.get("new_name","").strip()
            with lock:
                nick_taken = new_user in nicknames.values()
            if not new_user:
                send_json(conn, {
                    "type": "system",
                    "text": "Kullanıcı ismi boş olamaz.\n",
                })
                continue
            if nick_taken:
                send_json(conn, {
                    "type":"system",
                    "text": "Bu kullanıcı adı zaten var.\n"
                })
                continue
            elif old_nickname == new_user:
                send_json(conn, {
                    "type": "system",
                    "text": "Lütfen farklı bir kullanıcı adı girin.\n",
                })
                continue
            else:
                with lock:
                    nicknames[conn] = new_user
                new_msg = f"{old_nickname} ismini {new_user} olarak değiştirdi."
                send_json(conn, {
                    "type": "system",
                    "text": "İsminiz değiştirildi.\n",
                })
                broadcast({
                    "type": "system",
                    "text": new_msg,
                }, conn)
                continue
        if data.get("type") == "command" and data.get("name") == "help":
            help_text = (
                "\nKomutlar:\n"
                "/users: Online kullanıcılar\n"
                "/nick (isim): İsim değiştirir\n"
                "/msg (user) (mesaj): DM'den mesaj atar\n"
                "exit: Çıkış\n"
            )
            send_json(conn, {
                "type": "system",
                "text": help_text,
            })
            continue

        if data.get("type") == "dm":
            target_name = data.get("to")
            text = data.get("text","")

            target_conn = None
            with lock:
                users = list(nicknames.items())
            for c, name in users:
                if name == target_name:
                    target_conn = c
                    break
            if target_conn:
                sender = get_nickname(conn)
                sender_msg = {
                    "type": "dm",
                    "text": f"\n(DM) {sender}: {text}",
                }
                my_msg = {
                    "type":"dm",
                    "text":f"(DM -> {target_name}): {text}"
                }
                send_json(conn,my_msg)
                send_json(target_conn, sender_msg)
            else:
                send_json(conn, {
                    "type": "system",
                    "text": "Kullanıcı bulunamadı.",
                })
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
