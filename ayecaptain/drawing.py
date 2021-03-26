import threading

import cairo
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib


class Pointer():
    def __init__(self, window, image_path, x=None, y=None, normalized=True):
        self._window = window
        self._img = cairo.ImageSurface.create_from_png(image_path)
        self.width, self.height = self._img.get_width(), self._img.get_height()
        self.move(x, y, normalized=normalized)

    def move(self, x, y, normalized=True):
        self.x, self.y = x, y
        if normalized and x is not None and y is not None:
            self.x *= self._window.width
            self.y *= self._window.height
        GLib.idle_add(self._window.queue_draw)


class OverlayWindow(Gtk.Window):
    def __init__(self, width, height, opacity=0):
        self.pointers = []
        self.width, self.height = width, height
        self.opacity = opacity
        Gtk.Window.__init__(self)
        self.x, self.y = 100, 200
        self.set_size_request(width, height)
        self.connect('draw', self.draw)

        self.set_resizable(False)
        self.set_keep_above(True)
        self.set_decorated(False)
        self.set_visual(self.get_screen().get_rgba_visual())
        self.set_app_paintable(True)
        self.show_all()

    def new_pointer(self, image_path, x=None, y=None):
        pointer = Pointer(self, image_path, x=x, y=y)
        self.pointers.append(pointer)
        return pointer

    def draw(self, widget, event):
        cr = widget.get_window().cairo_create()
        if self.opacity:
            cr.set_source_rgba(0, 0, 0, self.opacity)
            cr.set_operator(cairo.OPERATOR_SOURCE)
            cr.paint()
            cr.set_operator(cairo.OPERATOR_OVER)

        for p in self.pointers:
            x, y = p.x, p.y
            if p.x is None or p.y is None:
                continue
            x, y = max(x, 0), max(y, 0)
            x, y = min(x, self.width), min(y, self.height)
            cr.set_source_surface(p._img,
                                  int(x - p.width / 2), int(y - p.height / 2))
            cr.paint()
        return False

    def connect_key_press_callback(self, callback):
        def cb(_, event, *a, **kwa):
            name = Gdk.keyval_name(event.keyval)
            callback(name)
        self.connect('key-press-event', cb)

    def connect_key_release_callback(self, callback):
        def cb(_, event, *a, **kwa):
            name = Gdk.keyval_name(event.keyval)
            callback(name)
        self.connect('key-release-event', cb)


threading.Thread(target=Gtk.main, daemon=True).start()
