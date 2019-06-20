import mock
import sys


def test_setup():
    sys.modules['RPi'] = mock.Mock()
    sys.modules['RPi.GPIO'] = mock.Mock()
    sys.modules['plasma'] = mock.Mock()

    from fanshim import FANShim
    fanshim = FANShim()
    del fanshim
