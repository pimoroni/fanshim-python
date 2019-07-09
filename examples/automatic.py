#!/usr/bin/env python3
from fanshim import FanShim
import psutil
import argparse
import time
import signal
import sys


parser = argparse.ArgumentParser()
parser.add_argument('--threshold', type=float, default=37.0, help='Temperature threshold in degrees C to enable fan')
parser.add_argument('--hysteresis', type=float, default=2.0, help='Distance from threshold before fan is disabled')
parser.add_argument('--delay', type=float, default=2.0, help='Delay, in seconds, between temperature readings')
parser.add_argument('--preempt', action='store_true', default=False, help='Monitor CPU frequency and activate cooling premptively')
parser.add_argument('--verbose', action='store_true', default=False, help='Output temp and fan status messages')
parser.add_argument('--nobutton', action='store_true', default=False, help='Disable button input')
parser.add_argument('--noled', action='store_true', default=False, help='Disable LED control')

args = parser.parse_args()


def clean_exit(signum, frame):
    set_fan(False)
    fanshim.set_light(0, 0, 0)
    sys.exit(0)


def update_led(state):
    if args.noled:
        return
    if state:
        fanshim.set_light(0, 255, 0)
    else:
        fanshim.set_light(255, 0, 0)


def get_cpu_temp():
    return psutil.sensors_temperatures()['cpu-thermal'][0].current


def get_cpu_freq():
    freq = psutil.cpu_freq()
    return freq


def set_fan(status):
    global enabled
    changed = False
    if status != enabled:
        changed = True
        update_led(status)
        fanshim.set_fan(status)
    enabled = status
    return changed


def set_automatic(status):
    global armed, last_change
    armed = status
    last_change = 0


fanshim = FanShim()
fanshim.set_hold_time(1.0)
fanshim.set_fan(False)
armed = True
enabled = False
last_change = 0

t = get_cpu_temp()
if t >= args.threshold:
    last_change = get_cpu_temp()
    set_fan(True)


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
        if args.noled:
             return
        for _ in range(3):
            fanshim.set_light(0, 0, 255)
            time.sleep(0.04)
            fanshim.set_light(0, 0, 0)
            time.sleep(0.04)
            update_led(enabled)


signal.signal(signal.SIGTERM, clean_exit)

try:
    update_led(fanshim.get_fan())
    while True:
        t = get_cpu_temp()
        f = get_cpu_freq()
        if args.verbose:
            print("Current: {:05.02f} Target: {:05.02f} Freq {: 5.02f} Automatic: {} On: {}".format(t, args.threshold, f.current / 1000.0, armed, enabled))
        if abs(last_change - t) > args.hysteresis and armed:
            enable = (t >= args.threshold)
            if args.preempt:
                enable = enable or (int(f.current) == int(f.max))
            if set_fan(enable):
                last_change = t
        time.sleep(args.delay)
except KeyboardInterrupt:
    pass
