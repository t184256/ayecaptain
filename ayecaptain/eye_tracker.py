import math
import socket

# consumes the protocol output by https://github.com/t184256/gaze-streamer


class EyeTracker:
    def __init__(self, host='localhost', port=10000, device=None):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self._sock.bind((host, port))
        self.device = device

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            data = self._sock.recv(128).decode()
            assert data.endswith('\n')
            data = data[:-1]
            url, t, x, y = data.split()
            if self.device is not None and url != self.device:
                continue
            assert t == 'gaze:'
            x, y = float(x), float(y)
            if math.isnan(x) or math.isnan(y):
                x, y = None, None
            return x, y
