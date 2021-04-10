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
        self.h = None

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            data = self._sock.recv(512).decode()
            assert data.endswith('\n')
            data = data[:-1]
            url, ts, typ, *rest = data.split()
            if self.device is not None and url != self.device:
                continue
            if typ == 'head_pos:':
                hx, hy, hz = rest
                hx, hy, hz = float(hx), float(hy), float(hz)
                if math.isnan(hx) or math.isnan(hy) or math.isnan(hz):
                    self.h = None
                else:
                    self.h = hx, hy, hz
                continue
            elif typ == 'gaze:':
                x, y = rest
                x, y = float(x), float(y)
                if math.isnan(x) or math.isnan(y):
                    x, y = None, None
                else:
                    if self.h is None:
                        x, y = None, None
                    else:
                        hx, hy, hz = self.h
                        # a one-eye'd head position correction model
                        # a tracker is positioned at bottom center + screen_d
                        # calibration is done for tracker mounted on screen
                        screen_w = 697  # mm, both real screen and pseudoscreen
                        screen_h = 392  # mm, both real screen and pseudoscreen
                        screen_d = 130  # mm, tracker-to-screen

                        x_pseudo_mm = (x - .5) * screen_w
                        y_pseudo_mm = (-y + .5) * screen_h

                        #                   *         ^
                        #   d  = x - hx     |\        | hz
                        #                   | \       v
                        # pseudoscreen  -+hx+dx\-------
                        #                |  |  |\     I screen_d
                        # real screen   -0--+--+-*-----
                        #                 \_____/
                        #                    ? = hx + dx * (hz + screen_d) / hz
                        # ? = hx + (x - hx) * (hz + screen_d) / hz
                        ratio = (hz + screen_d) / hz  # between triangles above
                        x_real_mm = hx + (x_pseudo_mm - hx) * ratio
                        y_real_mm = hy + (y_pseudo_mm - hy) * ratio

                        xn = x_real_mm / screen_w + .5
                        yn = -(y_real_mm / screen_h - .5)

                        x, y = xn, yn

                return x, y
