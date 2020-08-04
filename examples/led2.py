#!/usr/bin/env python3
from fanshim import FanShim
import time
import colorsys

fanshim = FanShim()
fanshim.set_fan(False)

try:
    for i in range(-10, 21):
        print("Temp index %d" % i)
        # Normal temperature range 0 to 1, cold < 0, hot > 1
        temp = i/10.0
        if temp < 0.0:
            # hue of blue through to green
            hue  = (120.0 / 360.0) - (temp * 120.0 / 360.0)
        elif temp > 1.0:
            # hue of red to through to magenta
            hue = ((1.0 - temp) * 60.0 / 360.0) + 1.0
        else:
            # hue of green through to red
            hue  = (1.0 - temp) * 120.0 / 360.0

        r, g, b = [int(c * 255.0) for c in colorsys.hsv_to_rgb(hue, 1.0, 1.0)]
        fanshim.set_light(r, g, b)

        time.sleep(1.0)

except KeyboardInterrupt:
    pass
