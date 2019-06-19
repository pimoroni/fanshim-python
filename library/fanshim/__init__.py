import RPi.GPIO as GPIO
from threading import Thread

__version__ = '0.0.1'


class FANShim():
    def __init__(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._pin_fancontrol, GPIO.OUT)
        GPIO.setup(self._pin_button, GPIO.IN)

        self._t_poll = Thread(target=self._run)
        self._t_poll.daemon = True
        self._t_poll.start()

        self._running = False

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

    def on_hold(self, handler=None, hold_time=2):
        self._button_hold_time = hold_time

        def attach_handler(handler):
            self._button_hold_handler = handler

        if handler is not None:
            attach_handler(handler)
        else:
            return attach_handler

    def _run(self):
        self._running = True
        last = 0

        while self._running:
            current = GPIO.input(self._pin_button)
            # Transition from 1 to 0
            if last > current:
                self._t_pressed = time.time()
                self._hold_fired = False

                if callable(self._button_press_handler):
                    self._t_repeat = time.time()
                    Thread(target=self._button_press_handler, args=(True,)).start()

            if last < current:
                if callable(self._button_release_handler):
                    Thread(target=self._button_release_handler, args=(False,)).start()

            if current == 0:
                if callable(self._button_hold_handler) and not self._hold_fired and (time.time() - self._t_pressed) > self._button_hold_time:
                    Thread(target=self._button_hold_handler, args(None,)).start()
                    self._hold_fired = True

            last = current

            time.sleep(0.001)

