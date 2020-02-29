# led.py

Basic demonstration of Fan Shim's RGB LED. Cycles around the circumference of the Hue/Saturation/Value colourspace.

# button.py

Demonstrates usage of button press, release and hold handlers.

# toggle.py

Demonstrates toggling the fan on and off with the button.

# manual.py

A barebones demonstration of how to control Fan SHIM manually.

Since a Python script writing a GPIO pin and exiting can have unpredictable effects, this example shows how you might craft a "service" that runs continuously and ensures the Fan's GPIO pin is asserted either on/off, and that the LED is continuously driven.

# automatic.py

Complete example for monitoring temperature and automatic fan control.

* A long press on the button will toggle automatic mode off/on
* A short press - when automatic is off - will toggle the fan

The LED will fade between green (cool) to red (hot) as the Pi's temperature changes.

The script supports these arguments:

* `--on-threshold N` the temperature at which to turn the fan on, in degrees C (default 65)
* `--off-threshold N` the temperature at which to turn the fan off, in degrees C (default 55)
* `--delay N` the delay between subsequent temperature readings, in seconds (default 2)
* `--preempt` preemptively kick in the fan when the CPU frequency is raised (default off)
* `--brightness` the brightness (value of HSV) of the LED (0-255, default 255)

Deprecated arguments

* `--threshold N` the temperature at which the fan should turn on, in degrees C (default 55)
* `--hysteresis N` the change in temperature needed to trigger a fan state change, in degrees C (default 5)

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
sudo ./install-service.sh --on-threshold 65 --off-threshold 55 --delay 2
```

To enable CPU-frequency based control:

```
sudo ./install-service.sh --on-threshold 65 --off-threshold 55 --delay 2 --preempt
```

You can also add `--noled` to disable LED control and/or `--nobutton` to disable button input.
