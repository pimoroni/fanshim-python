from fanshim import FANShim
import psutil
import argparse
import time


def update_led(state):
    if state:
        fanshim.set_light(0, 255, 0)
    else:
        fanshim.set_light(255, 0, 0)


def get_cpu_temp():
    return psutil.sensors_temperatures()['cpu-thermal'][0].current


def set_fan(status):
    global enabled
    changed = False
    if status != enabled:
        changed = True
    enabled = status
    update_led(enabled)
    fanshim.set_fan(enabled)
    return changed


parser = argparse.ArgumentParser()
parser.add_argument('--threshold', type=float, default=37.0, help='Temperature threshold in degrees C to enable fan')
parser.add_argument('--hysteresis', type=float, default=2.0, help='Distance from threshold before fan is disabled')

args = parser.parse_args()

fanshim = FANShim()
fanshim.set_fan(False)
enabled = False
last_change =0

t = get_cpu_temp()
if t >= args.threshold:
    last_change = get_cpu_temp()
    set_fan(True)


@fanshim.on_release()
def release_handler(was_held):
    global enabled
    enabled = not enabled
    update_led(enabled)


try:
    update_led(fanshim.get_fan())
    while True:
        t = get_cpu_temp()
        print("Current: {:05.02f} Target: {:05.02f}".format(t, args.threshold))
        if abs(last_change - t) > args.hysteresis:
            if set_fan(t >= args.threshold):
                last_change = t
        time.sleep(1.0)
except KeyboardInterrupt:
    pass
