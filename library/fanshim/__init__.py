import RPi.GPIO as GPIO
import time
import plasma
from threading import Thread

__version__ = '0.0.1'


class FANShim():
    def __init__(self):
        self._pin_fancontrol = 18 
        self._pin_button = 17
        self._button_press_handler = None
        self._button_release_handler = None
        self._button_hold_handler = None
        self._t_poll = None
        
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._pin_fancontrol, GPIO.OUT)
        GPIO.setup(self._pin_button, GPIO.IN)

        plasma.set_light_count(1)
        plasma.set_light(0, 0, 0, 0)

        self.start()

    def start(self):
        if self._t_poll is None:
            self._t_poll = Thread(target=self._run)
            self._t_poll.daemon = True
            self._t_poll.start()

    def stop(self):
        if self._t_poll is not None:
            self._running = False
            self._t_poll.stop()

    def on_press(self, handler=None):
        def attach_handler(handler):
            self._button_press_handler =handler

        if handler is not None:
            attach_handler(handler)
        else:
            return attach_handler

    def on_release(self, handler=None):
        def attach_handler(handler):
            self._button_release_handler = handler

        if handler is not None:
            attach_handler(handler)
        else:
            return attach_handler

    def on_hold(self, handler=None):
        def attach_handler(handler):
            self._button_hold_handler = handler

        if handler is not None:
            attach_handler(handler)
        else:
            return attach_handler

    def set_hold_time(self, hold_time):
        """Set the button hold time in seconds.
        
        :param hold_time: Amount of time button must be held to trigger on_hold (in seconds)

        """
        self._button_hold_time = hold_time

    def get_fan(self):
        return GPIO.input(self._pin_fancontrol)

    def toggle_fan(self):
        return self.set_fan(False if self.get_fan() else True)

    def set_fan(self, fan_state):
        """Set the fan on/off.
        
        :param fan_state: True/False for on/off
        
        """
        GPIO.output(self._pin_fancontrol, True if fan_state else False)
        return True if fan_state else False

    def set_light(self, r, g, b):
        plasma.set_light(0, r, g, b)
        plasma.show()

    def _run(self):
        self._running = True
        last = 1

        while self._running:
            current = GPIO.input(self._pin_button)
            # Transition from 1 to 0
            if last > current:
                self._t_pressed = time.time()
                self._hold_fired = False

                if callable(self._button_press_handler):
                    self._t_repeat = time.time()
                    Thread(target=self._button_press_handler).start()

            if last < current:
                if callable(self._button_release_handler):
                    Thread(target=self._button_release_handler, args=(self._hold_fired,)).start()

            if current == 0:
                if callable(self._button_hold_handler) and not self._hold_fired and (time.time() - self._t_pressed) > self._button_hold_time:
                    Thread(target=self._button_hold_handler).start()
                    self._hold_fired = True

            last = current

            time.sleep(0.001)

