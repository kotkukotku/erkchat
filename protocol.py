import json

def send_json(sock,data):
    sock.sendall((json.dumps(data)+"\n").encode())