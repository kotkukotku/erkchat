import json

def send_json(sock,data):
    try:
        sock.sendall((json.dumps(data)+"\n").encode())
    except Exception:
        pass