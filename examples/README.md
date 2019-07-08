# led.py

Basic demonstration of Fan Shim's RGB LED. Cycles around the circumference of the Hue/Saturation/Value colourspace.

# button.py

Demonstrates usage of button press, release and hold handlers.

# toggle.py

Demonstrates toggling the fan on and off with the button.

# automatic.py

Complete example for monitoring temperature and automatic fan control.

* A long press on the button will toggle automatic mode off/on
* A short press - when automatic is off - will toggle the fan

The LED should light up Green when the fan is enabled, and Red when it's not.

The script supports three arguments:

* `--threshold N` the temperature at which the fan should turn on, in degrees C
* `--hysteresis N` the change in temperature needed to trigger a fan state change, in degrees C
* `--delay N` the delay between subsequent temperature readings, in seconds
* `--preempt` preemptively kick in the fan when the CPU frequency is raised

You can use systemd or crontab to run this example as a fan controller service on your Pi.

To use systemd, just run:

```
sudo ./install-service.sh
```

You can then stop the fan service with:

```
sudo systemctl stop pimoroni-fanshim.service
```

If you need to change the threshold, hysteresis or delay you can add them as arguments to the installer:

```
sudo ./install-service.sh --threshold <threshold> --hysteresis <hysteresis> --delay <delay>
```

To enable CPU-frequency based control:

```
sudo ./install-service.sh --threshold <threshold> --hysteresis <hysteresis> --delay <delay> --preempt
```
