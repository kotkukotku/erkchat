import socket
import threading
import json

try:
    ip = input("Enter IP address:")
    port = 4444
    s = socket.socket()
    s.connect((ip,port))
except Exception as e:
    print("Connection error:",e)
    exit()
def listen():
    while True:
        try:
            cevap = s.recv(1024).decode(errors="ignore").strip()
            try:
                data = json.loads(cevap)
            except:
                print(cevap)
                continue
        except ConnectionResetError:
            print("Bağlantı koptu.")
            break
        if not data:
            print("Sunucuyla bağlantı koptu.")
            break
        if data["type"] == "system":
            if data["event"] == "shutdown":
                print(data.get("text"))
                break
            else:
                print(data.get("text"))
        if data["type"] == "dm":
            print(data.get("text"))
        if data["type"] == "chat":
            print(data.get("text"))
        
threading.Thread(target=listen,daemon=True).start()
nickname = input("Kullanıcı adı girin: ")
s.sendall(nickname.encode())
while True:
    msg = input()

    if msg == "exit":
        data = {
            "type":"exit",
        }
        s.sendall(json.dumps(data).encode())
        break
    elif msg == "/users":
        data = {
            "type":"command",
            "name": "users"
        }
    elif msg.startswith("/nick "):
        parts = msg.split(" ",1)
        if len(parts) < 2:
            print("Kullanım: /nick (Yeni Kullanıcı Adı)")
            continue
        data = {
            "type":"nick",
            "new_name":parts[1]
        }

    elif msg.startswith("/msg "):
        parts = msg.split(" ",2)
        if len(parts) < 3:
            print("Kullanım: /msg (Kullanıcı Adı) (Mesaj)")
            continue
        to = parts[1]
        text = parts[2]
        data = {
            "type":"dm",
            "to":to,
            "text":text
        }
    elif msg == "/help":
        data = {
            "type":"command",
            "name":"help"
        }
        s.sendall(json.dumps(data).encode())
        continue
    else:
        data = {
            "type": "msg",
            "text": msg
        }
    s.sendall(json.dumps(data).encode())
s.close()
