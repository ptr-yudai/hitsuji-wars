import socket
import json
import random

class Socket(object):
    def __init__(self, host: str, port: int):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

    def _sendline(self, raw: bytes):
        assert b'\n' not in raw, "Do not include newline"
        self.sock.sendall(raw + b'\n')

    def _recvline(self):
        data = b''
        while True:
            c = self.sock.recv(1)
            if c == b'':
                raise ConnectionRefusedError("Connection closed")
            if c == b'\n':
                break
            data += c
        return data

    def send_data(self, data: dict):
        self._sendline(json.dumps(data).encode())

    def recv_data(self):
        data = json.loads(self._recvline())
        if data['result'] == 'error':
            raise Exception(data['reason'])
        elif data['result'] == 'abort':
            raise Exception(data['reason'])
        return data['type'], data['data']

    def join(self, game: str, name=None):
        if name is None:
            name = "bot-{:08x}".format(random.randint(0, 0xffffffff))
        self.name = name
        self.send_data({'game':game, 'name':name})

    def close(self):
        self.sock.close()
        self.sock = None
