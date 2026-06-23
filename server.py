import socket
import threading
import collections
import json


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


def broadcast(new_msg, sender_client):
    for client in clients.copy():
        if sender_client != client:
            try:
                send_json(client, new_msg)
            except:
                reseting(client)


def reseting(conn):
    try:
        clients.remove(conn)
    except:
        pass
    nicknames.pop(conn, None)


def receive(conn, addr):
    f = conn.makefile("r", encoding="utf-8", errors="ignore")

    try:
        nickname = f.readline().strip()
        if not nickname:
            raise Exception("Kullanıcı adı belirtilmedi.")
        if nickname in nicknames.values():
            send_json(conn,{
                "type":"system",
                "event":"shutdown",
                "text":"Bu kullanıcı adı zaten var."
            })
            conn.close()
            reseting(conn)
            return
        print(nickname, "bağlandı.")
        nicknames[conn] = nickname
        broadcast({
            "type": "system",
            "text": f"{nicknames[conn]} bağlandı.",
        }, conn)
    except:
        conn.close()
        reseting(conn)
        return

    if message_log:
        send_json(conn, {
            "type": "system",
            "text": "--GEÇMİŞ MESAJLAR--\n",
        })
        for old_msg in message_log:
            send_json(conn, old_msg)
        send_json(conn, {
            "type": "system",
            "text": "-----------------------",
        })

    while True:
        raw = f.readline()
        if not raw:
            nickname = nicknames.get(conn)
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

            new_msg = {
                "type": "chat",
                "text": f"{nicknames[conn]}: {text}",
            }
            message_log.append(new_msg)
            broadcast(new_msg, conn)
            continue

        if data.get("type") == "exit":
            nickname = nicknames.get(conn)
            broadcast({
                "type": "system",
                "text": f"{nickname} ayrıldı.",
            }, conn)
            shut_msg = {
                "type": "system",
                "event": "shutdown",
                "text": "Server kapatıldı.",
            }
            send_json(conn, shut_msg)
            reseting(conn)
            conn.close()
            break

        if data.get("type") == "command" and data.get("name") == "users":
            user_list = "\n".join(nicknames.values())
            users_msg = {
                "type": "system",
                "text": f"Online users:\n{user_list}",
            }
            send_json(conn, users_msg)
            continue

        if data.get("type") == "nick":
            old_nickname = nicknames.get(conn)
            new_user = data["new_name"].strip()
            if not new_user:
                send_json(conn, {
                    "type": "system",
                    "text": "Kullanıcı ismi boş olamaz.",
                })
                continue
            elif old_nickname == new_user:
                send_json(conn, {
                    "type": "system",
                    "text": "Lütfen farklı bir kullanıcı adı girin.",
                })
                continue
            elif new_user in nicknames.values():
                send_json(conn, {
                    "type":"system",
                    "text": "Bu kullanıcı adı zaten var."
                })
                continue
            else:
                nicknames[conn] = new_user
                new_msg = f"{old_nickname} ismini {new_user} olarak değiştirdi."
                send_json(conn, {
                    "type": "system",
                    "text": "İsminiz değiştirildi.",
                })
                broadcast({
                    "type": "system",
                    "text": new_msg,
                }, conn)
                continue
        if data.get("type") == "command" and data.get("name") == "help":
            help_text = (
                "Komutlar:\n"
                "/users: Online kullanıcılar\n"
                "/nick (isim): İsim değiştirir\n"
                "/msg (user) (mesaj): DM'den mesaj atar\n"
                "exit: Çıkış"
            )
            send_json(conn, {
                "type": "system",
                "text": help_text,
            })
            continue

        if data.get("type") == "dm":
            target_name = data.get("to")
            text = data.get("text")

            target_conn = None
            for c, name in nicknames.items():
                if name == target_name:
                    target_conn = c
                    break
            if target_conn:
                sender = nicknames[conn]
                sender_msg = {
                    "type": "dm",
                    "text": f"(DM) {sender}: {text}",
                }
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
            clients.append(conn)
            threading.Thread(target=receive, args=(conn, addr), daemon=True).start()
        except OSError:
            break
except KeyboardInterrupt:
    print("\nCtrl+C algılandı. Server kapatılıyor.")
finally:
    print("Bağlantılar sonlandırılıyor...")
    for client in clients.copy():
        try:
            send_json(client, {
                "type": "system",
                "event": "shutdown",
                "text": "Server kapatıldı.",
            })
            client.close()
        except:
            pass
    s.close()
    print("Server güvenli şekilde kapatıldı.")
