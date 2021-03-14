#!/usr/bin/env python3

import math
import threading
import socket
import sys

import cairo
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject, GLib

HOST, PORT = sys.argv[1], int(sys.argv[2])

WIDTH, HEIGHT = 2560, 1440

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

DEVICES = {
        # REDACTED
        'tobii-ttp://IS404-000000000000': True,  # upside down
        'tobii-ttp://IS404-000000000000': False,  # normal
}


class Pointer():
    def __init__(self, image_path, x=None, y=None):
        self.x, self.y = x, y
        self._img = cairo.ImageSurface.create_from_png(image_path)

    def move(self, x, y):
        self.x, self.y = x, y
        GLib.idle_add(self._drawing_window.queue_draw)


class DrawingWindow(Gtk.Window):
    def draw(self, widget, event):
        cr = widget.get_window().cairo_create()
        #cr.set_source_rgba(0, 0, 0, 0.25)
        #cr.set_operator(cairo.OPERATOR_SOURCE)
        #cr.paint()
        #cr.set_operator(cairo.OPERATOR_OVER)

        for p in self.pointers:
            x, y = p.x, p.y
            if p.x is None or p.y is None:
                continue
            x, y = max(x, 0), max(y, 0)
            x, y = min(x, WIDTH), min(y, HEIGHT)
            cr.set_source_surface(p._img, int(x - 16), int(y - 16))
            cr.paint()
        return False

    def __init__(self, pointers):
        # self.image_path = image_path
        self.pointers = pointers
        for p in self.pointers:
            p._drawing_window = self
        Gtk.Window.__init__(self)
        self.x, self.y = 100, 200
        self.set_size_request(WIDTH, HEIGHT)
        #drawingarea = Gtk.DrawingArea()
        #self.add(drawingarea)
        #drawingarea.connect('draw', self.on_draw)
        self.connect('draw', self.draw)

        self.set_resizable(False)
        #self.set_keep_above(True)
        #self.set_decorated(False)
        self.set_visual(self.get_screen().get_rgba_visual())
        self.set_app_paintable(True)
        #self.connect('key-press-event', self.key_press_event)
        #image = Gtk.Image.new_from_file(image_path)
        #self.add(image)
        # self.set_visible(False)
        self.show_all()

p1 = Pointer('images/eye_red.png')
p2 = Pointer('images/eye_green.png')
p3 = Pointer('images/eye.png')
dw = DrawingWindow([p1, p2, p3])
threading.Thread(target=Gtk.main).start()


while True:
    data = sock.recv(128).decode()
    assert data.endswith('\n')
    data = data[:-1]
    url, t, x, y = data.split()
    assert t == 'gaze:'
    upside_down = DEVICES[url]
    x, y = float(x), float(y)
    if math.isnan(x) or math.isnan(y):
        x, y = None, None
    else:
        if upside_down:
            x = 1 - x
            y = 1 - y
        x *= WIDTH
        y *= HEIGHT
    #print(f'{url} {x:+.15f}, {y:+.15f}')
    if upside_down:
        p1.move(x, y)
        pass
    else:
        p2.move(x, y)
        pass
    if p1.x is None or p1.y is None or p2.x is None or p2.y is None:
        p3.move(None, None)
    else:
        p3.move((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)
