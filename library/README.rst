Fan Shim for Raspberry Pi
=========================

`Build Status <https://travis-ci.com/pimoroni/fanshim-python>`__
`Coverage
Status <https://coveralls.io/github/pimoroni/fanshim-python?branch=master>`__
`PyPi Package <https://pypi.python.org/pypi/fanshim>`__ `Python
Versions <https://pypi.python.org/pypi/fanshim>`__

Installing
==========

Stable library from PyPi:

-  Just run ``sudo pip install fanshim``

Latest/development library from GitHub:

-  ``git clone https://github.com/pimoroni/fanshim-python``
-  ``cd fanshim-python``
-  ``sudo ./install.sh``

Reference
=========

You should first set up an instance of the ``FANShim`` class, eg:

.. code:: python

   from fanshim import FanShim
   fanshim = FanShim()

Fan
---

Turn the fan on with:

.. code:: python

   fanshim.set_fan(True)

Turn it off with:

.. code:: python

   fanshim.set_fan(False)

You can also toggle the fan with:

.. code:: python

   fanshim.toggle_fan()

LED
---

Fan Shim includes one RGB APA-102 LED.

Set it to any colour with:

.. code:: python

   fanshim.set_light(r, g, b)

Arguments r, g and b should be numbers between 0 and 255 that describe
the colour you want.

For example, full red:

::

   fanshim.set_light(255, 0, 0)

Button
------

Fan Shim includes a button, you can bind actions to press, release and
hold events.

Do something when the button is pressed:

.. code:: python

   @fanshim.on_press()
   def button_pressed():
       print("The button has been pressed!")

Or when it has been released:

.. code:: python

   @fanshim.on_release()
   def button_released(was_held):
       print("The button has been pressed!")

Or when it’s been pressed long enough to trigger a hold:

.. code:: python

   fanshim.set_hold_time(2.0)

   @fanshim.on_hold()
   def button_held():
       print("The button was held for 2 seconds")

The function you bind to ``on_release()`` is passed a ``was_held``
parameter, this lets you know if the button was held down for longer
than the configured hold time. If you want to bind an action to “press”
and another to “hold” you should check this flag and perform your action
in the ``on_release()`` handler:

.. code:: python

   @fanshim.on_release()
   def button_released(was_held):
       if was_held:
           print("Long press!")
       else:
           print("Short press!")

To configure the amount of time the button should be held (in seconds),
use:

.. code:: python

   fanshim.set_hold_time(number_of_seconds)

If you need to stop Fan Shim from polling the button, use:

.. code:: python

   fanshim.stop_polling()

You can start it again with:

.. code:: python

   fanshim.start_polling()

0.0.2

* Fix: Fix error on exit

0.0.1
-----

* Initial Release
