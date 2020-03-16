import mock
import sys


def force_reimport(module):
    """Force the module under test to be re-imported.

    Because pytest runs all tests within the same scope (this makes me cry)
    we have to do some manual housekeeping to avoid tests polluting each other.

    In this case, the first `from fanshim import FanShim` would import both plasma
    and RPi.GPIO from the first test run fixtures. Since we want *clean* fixtures
    for each test this is not only no good but the results are outright weird-

    IE: functions we expect to be called will have no calls because FanShim
    receives an entirely different mock object to the one we're validating against.

    Since conftest.py already does some sys.modules mangling I see no reason not to
    do the same thing here.
    """
    try:
        del sys.modules[module]
    except KeyError:
        pass


def test_setup(GPIO, plasma):
    force_reimport('fanshim')

    from fanshim import FanShim
    fanshim = FanShim()

    GPIO.setwarnings.assert_called_once_with(False)
    GPIO.setmode.assert_called_once_with(GPIO.BCM)
    GPIO.setup.assert_has_calls([
        mock.call(fanshim._pin_fancontrol, GPIO.OUT),
        mock.call(fanshim._pin_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    ])

    plasma.legacy.set_clear_on_exit.assert_called_once_with(True)
    plasma.legacy.set_light_count.assert_called_once_with(1)
    plasma.legacy.set_light.assert_called_once_with(0, 0, 0, 0)


def test_button_disable(GPIO, plasma):
    force_reimport('fanshim')

    from fanshim import FanShim
    fanshim = FanShim(disable_button=True)

    GPIO.setwarnings.assert_called_once_with(False)
    GPIO.setmode.assert_called_once_with(GPIO.BCM)
    GPIO.setup.assert_called_once_with(fanshim._pin_fancontrol, GPIO.OUT)


def test_led_disable(GPIO, plasma):
    force_reimport('fanshim')

    from fanshim import FanShim
    fanshim = FanShim(disable_led=True)

    GPIO.setwarnings.assert_called_once_with(False)
    GPIO.setmode.assert_called_once_with(GPIO.BCM)
    GPIO.setup.assert_has_calls([
        mock.call(fanshim._pin_fancontrol, GPIO.OUT),
        mock.call(fanshim._pin_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    ])

    plasma.legacy.set_clear_on_exit.assert_not_called()
    plasma.legacy.set_light_count.assert_not_called()
    plasma.legacy.set_light.assert_not_called()

    fanshim.set_light(0, 0, 0)
    plasma.legacy.set_light.assert_not_called()
    plasma.legacy.show.assert_not_called()
