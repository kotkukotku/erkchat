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
s.bind((ip,port))
s.listen()
def broadcast(new_msg,sender_client):
    for client in clients.copy():
        if sender_client != client:
            try:
                client.sendall(new_msg.encode())
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
        broadcast(f"{nicknames[conn]} bağlandı.",conn)    
    except:
        conn.close()
        clients.remove(conn)
        return
    if message_log:
        conn.sendall("--GEÇMİŞ MESAJLAR--\n".encode())
        for old_msg in message_log:
            conn.sendall(f"{old_msg}\n".encode())
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
            
            new_msg = f"{nicknames[conn]}: {text}"
            message_log.append(new_msg)
            broadcast(new_msg,conn)
            continue
        if data["type"] == "exit":
            nickname = nicknames.get(conn)
            broadcast(f"{nickname} ayrıldı.",conn)
            
            reseting(conn)
            conn.close()
            break
        if data["type"] == "command" and data["name"] == "users":
            user_list = "\n".join(nicknames.values())
            conn.sendall(f"Online users:\n{user_list}".encode())
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
                target_conn.sendall(f"(DM) {sender}: {text}".encode())
            else:
                conn.sendall("Kullanıcı bulunamadı.".encode())
            continue
while True:
    conn, addr = s.accept()
    clients.append(conn)
    threading.Thread(target=receive,args=(conn,addr),daemon=True).start()
s.close()
