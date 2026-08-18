import json

def send_json(sock, data):
    try:
        sock.sendall((json.dumps(data, ensure_ascii=False) + "\n").encode("utf-8"))
        return True
    except OSError:
        return False