TradersBot
======================================
.. autoclass:: tradersbot.TradersBot	
    :members: run, addPeriodicCallback

TradersBot Callbacks
--------------------------------------
Before calling ``run``, you should set the callbacks for each message type
that you want to listen to. If you set the callback for message type `x` to
be your function `f`, `f` will be called whenever a message of type `x` is
received from the MangoCore server. The callbacks are listed below.

.. autoclass:: tradersbot.TradersBot
	:noindex:
	:members:
	:exclude-members: run, addPeriodicCallback
