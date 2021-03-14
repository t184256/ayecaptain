#!/usr/bin/env python3

import sys

import ayecaptain.drawing
import ayecaptain.eye_tracker

HOST, PORT, WIDTH, HEIGHT, DEVICE = sys.argv[1:]
PORT, WIDTH, HEIGHT = int(PORT), int(WIDTH), int(HEIGHT)

et = ayecaptain.eye_tracker.EyeTracker(HOST, PORT, DEVICE)

ow = ayecaptain.drawing.OverlayWindow(WIDTH, HEIGHT)
p1 = ow.new_pointer('images/eye_red.png')
p2 = ow.new_pointer('images/eye_green.png')
p3 = ow.new_pointer('images/eye.png')


for x, y in et:
    if x is None or y is None:
        #print('-')
        p1.move(None, None)
    else:
        #print(f'{url} {x:+.15f}, {y:+.15f}')
        p1.move(x * WIDTH, y * HEIGHT)
