#!/usr/bin/env python3

import sys

import numpy as np

import ayecaptain.corrector
import ayecaptain.drawing
import ayecaptain.eye_tracker

HOST, PORT, WIDTH, HEIGHT, DEVICE = sys.argv[1:]
PORT, WIDTH, HEIGHT = int(PORT), int(WIDTH), int(HEIGHT)

LEARNING_WEIGHT = 1/3
SIGMA = 1/30  # of the screen width
CORRECTION_CAP = 1/100  # of the screen width
SAVE_EACH = 5
SHOW_CURRENT = False


ow = ayecaptain.drawing.OverlayWindow(WIDTH, HEIGHT)
p_raw = ow.new_pointer('images/eye_blue.png')
p_current = ow.new_pointer('images/eye_red.png')
p_counterweight = ow.new_pointer('images/eye.png')
p_pivot = ow.new_pointer('images/eye_green.png')

compensating = False
pivot_point_x, pivot_point_y = None, None
pivot_point_x_raw, pivot_point_y_raw = None, None  # pre-Corrector
current_x_raw, current_y_raw = None, None  # pre-Corrector
current_x, current_y = None, None  # post-Corrector


corrector = ayecaptain.corrector.Corrector(WIDTH//2, HEIGHT//2, SIGMA,
                                           CORRECTION_CAP, save_each=SAVE_EACH,
                                           path='correction.npz')


def key_press_callback(key):
    global compensating
    global pivot_point_x, pivot_point_y
    global pivot_point_x_raw, pivot_point_y_raw
    global current_x, current_y
    global current_x_raw, current_y_raw
    if key == 'e':
        if not compensating and current_x is not None and current_y is not None:
            compensating = True
            pivot_point_x_raw, pivot_point_y_raw = current_x_raw, current_y_raw
            pivot_point_x, pivot_point_y = current_x, current_y
            print('compensation started', pivot_point_x, pivot_point_y)


def key_release_callback(key):
    global compensating
    global pivot_point_x, pivot_point_y
    global pivot_point_x_raw, pivot_point_y_raw
    global current_x, current_y
    global current_x_raw, current_y_raw
    if key == 'e':
        print('release')
        if compensating and current_x is not None and current_y is not None:
            compensation_x = pivot_point_x_raw - current_x_raw
            compensation_y = pivot_point_y_raw - current_y_raw
            print('learning')
            corrector.learn(current_x_raw, current_y_raw,
                            compensation_x, compensation_y,
                            weight=LEARNING_WEIGHT)
            print('compensation done')
            compensating = False
            pivot_point_x_raw, pivot_point_y_raw = None, None
            pivot_point_x, pivot_point_y = None, None


ow.connect_key_press_callback(key_press_callback)
ow.connect_key_release_callback(key_release_callback)


def median_filter(gen, n_min, n_max):
    xs, ys = [], []
    for x, y in gen:
        if x is None or y is None:
            xs, ys = [], []
            continue
        xs.append(x)
        ys.append(y)
        xs = xs[-n_max:]
        ys = ys[-n_max:]
        ln = len(xs)
        if ln > n_min:
            yield np.median(xs), np.median(ys)
        else:
            yield None, None


tracker = ayecaptain.eye_tracker.EyeTracker(HOST, PORT, DEVICE)
tracker = median_filter(tracker, n_min=15, n_max=30)

for x, y in tracker:
    if x is None or y is None:
        if SHOW_CURRENT:
            p_raw.move(None, None)
            p_current.move(None, None)
        p_counterweight.move(None, None)
        current_x_raw, current_y_raw = None, None
        current_x, current_y = None, None
        continue

    if SHOW_CURRENT:
        p_raw.move(x, y)
    current_x_raw, current_y_raw = x, y
    current_x, current_y = corrector.correct(x, y)
    if SHOW_CURRENT:
        p_current.move(current_x, current_y)

    if compensating:
        compensation_x = current_x - pivot_point_x
        compensation_y = current_y - pivot_point_y
        counterweight_x = pivot_point_x - compensation_x
        counterweight_y = pivot_point_y - compensation_y
        p_pivot.move(pivot_point_x, pivot_point_y)
        p_counterweight.move(counterweight_x, counterweight_y)
    else:
        p_pivot.move(None, None)
        p_counterweight.move(None, None)
