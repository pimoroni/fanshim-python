#!/usr/bin/env python3
from fanshim import FanShim
import time
import colorsys

fanshim = FanShim()
fanshim.set_fan(False)

try:
    while True:
        h = time.time() / 25.0
        r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(h, 1.0, 1.0)]
        fanshim.set_light(r, g, b, brightness=0.05)
        time.sleep(1.0 / 60)

except KeyboardInterrupt:
    pass
