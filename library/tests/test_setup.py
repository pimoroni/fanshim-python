import mock
import sys


def test_setup(GPIO, apa102, FanShim):
    fanshim = FanShim()

    GPIO.setwarnings.assert_called_once_with(False)
    GPIO.setmode.assert_called_once_with(GPIO.BCM)
    GPIO.setup.assert_has_calls([
        mock.call(fanshim._pin_fancontrol, GPIO.OUT),
        mock.call(fanshim._pin_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    ])

    apa102.APA102.assert_called_once_with(1, 15, 14, None, brightness=0.05)


def test_button_disable(GPIO, apa102, FanShim):
    fanshim = FanShim(disable_button=True)

    GPIO.setwarnings.assert_called_once_with(False)
    GPIO.setmode.assert_called_once_with(GPIO.BCM)
    GPIO.setup.assert_called_once_with(fanshim._pin_fancontrol, GPIO.OUT)


def test_led_disable(GPIO, apa102, FanShim):
    fanshim = FanShim(disable_led=True)

    GPIO.setwarnings.assert_called_once_with(False)
    GPIO.setmode.assert_called_once_with(GPIO.BCM)
    GPIO.setup.assert_has_calls([
        mock.call(fanshim._pin_fancontrol, GPIO.OUT),
        mock.call(fanshim._pin_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    ])

    assert not apa102.APA102.called

    fanshim.set_light(0, 0, 0)
