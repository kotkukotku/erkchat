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
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
s.bind((ip,port))
s.listen()
def broadcast(new_msg,sender_client):
    for client in clients.copy():
        if sender_client != client:
            try:
                client.sendall(json.dumps(new_msg).encode())
            except:
                reseting(client)
def reseting(conn):
    try:
        clients.remove(conn)
    except:
        pass
    nicknames.pop(conn,None)
def receive(conn,addr):
    try:
        nickname = conn.recv(1024).decode(errors="ignore").strip()
        if not nickname:
            raise Exception("Kullanıcı adı belirtilmedi.")
        print(nickname, "bağlandı.")
        nicknames[conn] = nickname
        broadcast({
            "type":"system",
            "text":f"{nicknames[conn]} bağlandı."
        },conn)    
    except:
        conn.close()
        clients.remove(conn)
        return
    if message_log:
        conn.sendall("--GEÇMİŞ MESAJLAR--\n".encode())
        for old_msg in message_log:
            conn.sendall(json.dumps(old_msg).encode() + b"\n")
        conn.sendall("-----------------------".encode())
    while True:
        raw = conn.recv(1024).decode(errors="ignore").strip()
        if not raw:
            reseting(conn)
            break
        try:
            data = json.loads(raw)
        except json.decoder.JSONDecodeError:
            reseting(conn)
            break
        if data["type"] == "msg":
            text = data["text"]
            
            new_msg = {
                "type":"chat",
                "text":f"{nicknames[conn]}: {text}"
            }
            message_log.append(new_msg)
            broadcast(new_msg,conn)
            continue
        if data["type"] == "exit":
            nickname = nicknames.get(conn)
            broadcast({
                "type":"system",
                "text":f"{nickname} ayrıldı."},conn)
            shut_msg = {
                "type":"system",
                "event":"shutdown",
                "text":"Server kapatıldı."
            }
            conn.sendall(json.dumps(shut_msg).encode())
            reseting(conn)
            conn.close()
            break
        if data["type"] == "command" and data["name"] == "users":
            user_list = "\n".join(nicknames.values())
            users_msg = {
                "type":"system",
                "text":f"Online users:\n{user_list}"}
            conn.sendall(json.dumps(users_msg).encode())
            continue
        if data["type"] == "nick":
            old_nickname = nicknames.get(conn)
            new_user = data["new_name"].strip()
            if not new_user:
                conn.sendall("Kullanıcı ismi boş olamaz.".encode())
                continue
            if old_nickname != new_user:
                nicknames[conn] = new_user
                new_msg = f"{old_nickname} ismini {new_user} olarak değiştirdi."
                
                broadcast({
                    "type":"system",
                    "text":new_msg},conn)
                continue
            else:
                conn.sendall("Lütfen farklı bir kullanıcı adı girin.".encode())
                continue
        if data["type"] == "command" and data["name"] == "help":
            help_text = (
                "Komutlar:\n"
                "/users: Online kullanıcılar\n"
                "/nick (isim): İsim değiştirir\n"
                "/msg (user) (mesaj): DM'den mesaj atar\n"
                "exit: Çıkış"
            )
            conn.sendall(json.dumps({
                "type":"system",
                "text":help_text}).encode())
            continue
        if data["type"] == "dm":
            target_name = data["to"]
            text = data["text"]

            target_conn = None
            for c,name in nicknames.items():
                if name == target_name:
                    target_conn = c
                    break
            if target_conn:
                sender = nicknames[conn]
                sender_msg = {
                    "type":"dm",
                    "text":f"(DM) {sender}: {text}"
                }
                target_conn.sendall(json.dumps(sender_msg).encode())
            else:
                conn.sendall(json.dumps({
                    "type":"system",
                    "text":f"Kullanıcı bulunamadı."}).encode())
            continue
print(f"Server {port} portunda başlatıldı. Kapatmak için Ctrl+C yapın.")
try:
    while True:
        try:
            conn, addr = s.accept()
            clients.append(conn)
            threading.Thread(target=receive,args=(conn,addr),daemon=True).start()
        except OSError:
            break
except KeyboardInterrupt:
    print("\nCtrl+C algılandı. Server kapatılıyor.")
finally:
    print("Bağlantılar sonlandırılıyor...")
    for client in clients.copy():
        try:
            client.sendall("Server kapatıldı.\n".encode())
            client.close()
        except:
            pass
    s.close()
    print("Server güvenli şekilde kapatıldı.")
