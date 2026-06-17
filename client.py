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
        except:
            print("Bağlantı koptu.")
            break
        if not cevap:
            print("Sunucuyla bağlantı koptu.")
            break
        if cevap == "exit":
            print("Server kapatıldı.")
            break
        print(cevap)
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
    else:
        data = {
            "type": "msg",
            "text": msg
        }
    s.sendall(json.dumps(data).encode())
s.close()
