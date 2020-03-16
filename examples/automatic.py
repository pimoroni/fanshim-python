#!/usr/bin/env python3
from fanshim import FanShim
from threading import Lock
import colorsys
import psutil
import argparse
import time
import signal
import sys


parser = argparse.ArgumentParser()
parser.add_argument('--off-threshold', type=float, default=55.0, help='Temperature threshold in degrees C to enable fan')
parser.add_argument('--on-threshold', type=float, default=65.0, help='Temperature threshold in degrees C to disable fan')
parser.add_argument('--low-temp', type=float, default=None, help='Temperature at which the LED is greeen')
parser.add_argument('--high-temp', type=float, default=None, help='Temperature for which LED is red')
parser.add_argument('--delay', type=float, default=2.0, help='Delay, in seconds, between temperature readings')
parser.add_argument('--preempt', action='store_true', default=False, help='Monitor CPU frequency and activate cooling premptively')
parser.add_argument('--verbose', action='store_true', default=False, help='Output temp and fan status messages')
parser.add_argument('--nobutton', action='store_true', default=False, help='Disable button input')
parser.add_argument('--noled', action='store_true', default=False, help='Disable LED control')
parser.add_argument('--brightness', type=float, default=255.0, help='LED brightness, from 0 to 255')
parser.add_argument('--extended-colours', action='store_true', default=False, help='Extend LED colours for outside of normal low to high range')

args = parser.parse_args()


def clean_exit(signum, frame):
    set_fan(False)
    if not args.noled:
        fanshim.set_light(0, 0, 0)
    sys.exit(0)


def update_led_temperature(temp):
    led_busy.acquire()
    temp = float(temp)
    if temp < args.low_temp and args.extended_colours:
        # Between minimum temp and low temp, set LED to blue through to green
        temp -= min_temp
        temp /= float(args.low_temp - min_temp)
        temp  = max(0, temp)
        hue   = (120.0 / 360.0) + ((1.0 - temp) * 120.0 / 360.0)
    elif temp > args.high_temp and args.extended_colours:
        # Between high temp and maximum temp, set LED to red through to magenta
        temp -= args.high_temp
        temp /= float(max_temp - args.high_temp)
        temp  = min(1, temp)
        hue   = 1.0 - (temp * 60.0 / 360.0)
    else:
        # In the normal low temp to high temp range, set LED to green through to red
        temp -= args.low_temp
        temp /= float(args.high_temp - args.low_temp)
        temp = max(0, min(1, temp))
        hue   = (1.0 - temp) * 120.0 / 360.0

    r, g, b = [int(c * 255.0) for c in colorsys.hsv_to_rgb(hue, 1.0, args.brightness / 255.0)]
    fanshim.set_light(r, g, b)
    led_busy.release()


def get_cpu_temp():
    t = psutil.sensors_temperatures()
    for x in ['cpu-thermal', 'cpu_thermal']:
        if x in t:
            return t[x][0].current
    print("Warning: Unable to get CPU temperature!")
    return 0


def get_cpu_freq():
    freq = psutil.cpu_freq()
    return freq


def set_fan(status):
    global enabled
    changed = False
    if status != enabled:
        changed = True
        fanshim.set_fan(status)
    enabled = status
    return changed


def set_automatic(status):
    global armed, last_change
    armed = status
    last_change = 0


fanshim = FanShim(disable_button=args.nobutton, disable_led=args.noled)
fanshim.set_hold_time(1.0)
fanshim.set_fan(False)
armed = True
enabled = False
led_busy = Lock()
enable = False
is_fast = False
last_change = 0
min_temp = 30
max_temp = 85
signal.signal(signal.SIGTERM, clean_exit)

if args.noled:
    led_busy.acquire()
    fanshim.set_light(0, 0, 0)
    led_busy.release()

if args.low_temp is None:
    args.low_temp = args.off_threshold

if args.high_temp is None:
    args.high_temp = args.on_threshold

if not args.nobutton:
    @fanshim.on_release()
    def release_handler(was_held):
        global armed
        if was_held:
            set_automatic(not armed)
        elif not armed:
            set_fan(not enabled)

    @fanshim.on_hold()
    def held_handler():
        global led_busy
        if args.noled:
            return
        led_busy.acquire()
        for _ in range(3):
            fanshim.set_light(0, 0, 255)
            time.sleep(0.04)
            fanshim.set_light(0, 0, 0)
            time.sleep(0.04)
        led_busy.release()


try:
    while True:
        t = get_cpu_temp()
        f = get_cpu_freq()
        was_fast = is_fast
        is_fast = (int(f.current) == int(f.max))
        if args.verbose:
            print("Current: {:05.02f} Target: {:05.02f} Freq {: 5.02f} Automatic: {} On: {}".format(t, args.off_threshold, f.current / 1000.0, armed, enabled))

        if args.preempt and is_fast and was_fast:
            enable = True
        elif armed:
            if t >= args.on_threshold:
                enable = True
            elif t <= args.off_threshold:
                enable = False

            if set_fan(enable):
                last_change = t

        if not args.noled:
            update_led_temperature(t)

        time.sleep(args.delay)
except KeyboardInterrupt:
    pass
