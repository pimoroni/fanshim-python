"""Test configuration.
These allow the mocking of various Python modules
that might otherwise have runtime side-effects.
"""
import sys
import mock
import pytest


@pytest.fixture(scope='function', autouse=False)
def FanShim():
    import fanshim
    yield fanshim.FanShim
    del sys.modules['fanshim']


@pytest.fixture(scope='function', autouse=False)
def GPIO():
    """Mock RPi.GPIO module."""
    GPIO = mock.MagicMock()
    # Fudge for Python < 37 (possibly earlier)
    sys.modules['RPi'] = mock.Mock()
    sys.modules['RPi'].GPIO = GPIO
    sys.modules['RPi.GPIO'] = GPIO
    yield GPIO
    del sys.modules['RPi']
    del sys.modules['RPi.GPIO']


@pytest.fixture(scope='function', autouse=False)
def apa102():
    """Mock APA102 module."""
    apa102 = mock.MagicMock()
    sys.modules['apa102'] = apa102
    yield apa102
    del sys.modules['apa102']


@pytest.fixture(scope='function', autouse=False)
def spidev():
    """Mock spidev module."""
    spidev = mock.MagicMock()
    sys.modules['spidev'] = spidev
    yield spidev
    del sys.modules['spidev']


@pytest.fixture(scope='function', autouse=False)
def atexit():
    """Mock atexit module."""
    atexit = mock.MagicMock()
    sys.modules['atexit'] = atexit
    yield atexit
    del sys.modules['atexit']

