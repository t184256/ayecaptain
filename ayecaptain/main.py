#!/usr/bin/env python3

import sys

import ayecaptain.drawing
import ayecaptain.eye_tracker

HOST, PORT, WIDTH, HEIGHT, DEVICE1, DEVICE2 = sys.argv[1:]
PORT, WIDTH, HEIGHT = int(PORT), int(WIDTH), int(HEIGHT)


ow = ayecaptain.drawing.OverlayWindow(WIDTH, HEIGHT)
p1 = ow.new_pointer('images/eye_blue.png')
p2 = ow.new_pointer('images/eye_red.png')


for uri, x, y in ayecaptain.eye_tracker.EyeTracker(HOST, PORT):
    p = p1 if uri.endswith('4') else p2
    print(uri, x, y)
    if x is None or y is None:
        p.move(None, None)

    p.move(x, y)
