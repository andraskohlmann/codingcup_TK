import json
import socket

SERVER_IP = '10.100.1.150'
SERVER_PORT = 12323
BUFFER_SIZE = 1024


class Communications:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __enter__(self):
        self.s.connect((SERVER_IP, SERVER_PORT))
        print('Connected to server')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.s.close()

    def send_and_receive(self, msg):
        self.s.send(json.dumps(msg).encode())
        response = self.s.recv(BUFFER_SIZE).decode()
        if len(response) > 0:
            return json.loads(response)
        return None
