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


def update_led(state):
    if state:
        fanshim.set_light(0, 255, 0)
    else:
        fanshim.set_light(255, 0, 0)


@fanshim.on_release()
def release_handler(was_held):
    state = fanshim.toggle_fan()
    update_led(state)


try:
    update_led(fanshim.get_fan())
    signal.pause()
except KeyboardInterrupt:
    pass
