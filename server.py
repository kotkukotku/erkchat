#server.py

import socket
import threading
import collections
import json
from datetime import datetime

import database
import auth
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

    auth_success = False
    current_nick = ""
    user_role = "user"

    while not auth_success:
        raw = f.readline()
        if not raw:
            reseting(conn)
            return
        try:
            data = json.loads(raw.strip())
        except json.JSONDecodeError:
            continue
        
        if data.get("type") == "auth":
            action = data.get("action")
            username = data.get("username","").strip()
            raw_password = data.get("password","").strip()
            if not username or not raw_password:
                send_json(conn, {"type": "auth_response",
                "success":False,
                "message": "Kullanıcı adı veya şifre boş olamaz."})
                continue
            if action == "register":
                if auth.register(username, raw_password):
                    send_json(conn, {"type": "auth_response",
                    "success":True,
                    "message": "Kayıt başarılı! Şimdi giriş yapın."})
                else:
                    send_json(conn, {"type": "auth_response",
                    "success":False,
                    "message": "Hata: Kullanıcı adı zaten alınmış."})
            elif action == "login":
                rol = auth.login(username, raw_password)
                if rol:
                    with lock:
                        if username in nicknames.values():
                            send_json(conn,{"type": "auth_response",
                            "success":False,
                            "message": "Bu hesap şu an zaten aktif!"})
                            continue
                        nicknames[conn] = username
                        current_nick = username
                        user_role = rol
                        auth_success = True
                    send_json(conn, {"type": "auth_response",
                    "success":True,
                    "message": f"Giriş Başarılı! Rolünüz: {user_role}"})
                    broadcast({"type": "system", "text": f"{current_nick} bağlandı."}, conn)
                else:
                    send_json(conn, {"type": "auth_response",
                    "success":False,
                    "message": "Hatalı kullanıcı adı veya şifre!"})

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
            text = data["text"]
            with lock:
                sender = nicknames.get(conn, "Unknown")
            current_time = datetime.now().strftime("%H:%M")
            new_msg = {
                "type": "chat",
                "text": f"[{current_time}] {sender}: {text}",
            }
            database.add_message(
                sender,
                text,
                None
            )
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
                    "text": "Bu kullanıcı adı şu an aktif birinde zaten var.\n"
                })
                continue
            elif old_nickname == new_user:
                send_json(conn, {
                    "type": "system",
                    "text": "Lütfen farklı bir kullanıcı adı girin.\n",
                })
                continue
            else:
                if database.update_username(old_nickname, new_user):
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
                else:
                    send_json(conn,{"type":"system",
                    "text":"Bu kullanıcı adı veritabanında kayıtlı.\n"})
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
