#!/usr/bin/env python
import sys
import os
from fanshim import FanShim

FIFO_NAME = "/tmp/fanshim"

fanshim = FanShim()
fanshim.set_hold_time(1.0)
fanshim.set_fan(False)

try:
    os.unlink(FIFO_NAME)
except (IOError, OSError):
    pass

os.mkfifo(FIFO_NAME)


def handle_command(data):
    if data == "on":
        fanshim.set_fan(True)
        print("Fan SHIM: Fan enabled")
    elif data == "off":
        fanshim.set_fan(False)
        print("Fan SHIM: Fan disabled")
    elif len(data) == 6:
        r, g, b = data[0:2], data[2:4], data[4:6]
        try:
            r, g, b = [int(c, 16) for c in (r, g, b)]
        except ValueError:
            print("Fan SHIM: Invalid colour {c}".format(c=data))
            return
        print("Fan SHIM: Setting LED to RGB: {r}, {g}, {b}".format(r=r, g=g, b=b))
        fanshim.set_light(r, g, b)


print("""manual.py - Fan SHIM manual control

Example commands:

    echo "on" > /tmp/fanshim     - Turn fan on
    echo "off" > /tmp/fanshim    - Turn fan off
    echo "FF0000" > /tmp/fanshim - Make LED red
    echo "00FF00" > /tmp/fanshim - Make LED green

""")

while True:
    with open(FIFO_NAME, "r") as fifo:
        while True:
            data = fifo.read().strip()
            if len(data) == 0:
                break
            handle_command(data)
