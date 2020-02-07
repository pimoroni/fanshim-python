#!/usr/bin/env python3
import signal
from fanshim import FanShim

"""
This example attaches basic pressed, released and held handlers for Fan SHIM's button.

If you want to use both a short press, and a long press you should use the "release"
handler to perform the actual action.

Since the "release" handler receives 1 argument - "was_held" - you don't need to bind
the "held" handler at all if you're just doing a standard short/long press action.
"""

fanshim = FanShim()

# Set the button hold time, in seconds
fanshim.set_hold_time(1.0)


@fanshim.on_press()
def press_handler():
    print("Pressed")


@fanshim.on_release()
def release_handler(was_held):
    print("Released")
    if was_held:
        print("Long press.")
    else:
        print("Short press.")


# Not needed to detect short/long press
# But included to demonstrate when it happens
@fanshim.on_hold()
def hold_handler():
    print("HELD")


try:
    signal.pause()
except KeyboardInterrupt:
    pass
