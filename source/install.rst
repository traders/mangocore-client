.. _install:

Installation and Example
======================================
Installation
--------------------------------------
Install Python and pip if needed. Find the appropriate Python
installer `here <https://www.python.org/downloads/>`_; if you
don't have pip (a Python package manager), type in the terminal
``easy_install pip`` to get pip. Then type ``pip install tradersbot``
to install the tradersbot package.

Initialization
--------------------------------------
First, import the ``tradersbot`` package and instantiate a ``TradersBot``.

.. code-block:: python

	from tradersbot import TradersBot
	t = TradersBot('18.247.12.164', 'MIT2', 'password')

The TradersBot takes in an IP/URL, a username, and a password. For
local testing (with your downloaded MangoCore binary from Dropbox)
the username and password are both `trader0`. Your actual username
and password for competition day will be emailed to you.

Optionally, you may include a token parameter to uniquely identify
this instance of your bot. See :ref:`tokens` for more details.

Adding Callbacks
--------------------------------------
TradersBot is based on callbacks; for each message type MangoCore
sends, you may specify a callback function which will be called
whenever TradersBot receives a message of that type from MangoCore.
Every callback function you write must take in two parameters;
the first will be the message MangoCore sent you, while the second
is an order object (initialized blank) that you call if you want
to make orders. See :ref:`callbacks` for all available callbacks
and exact specifications on the format of the JSON message for each
callback, and :ref:`TradersOrder` for details on how to interact
with the order object.

A few examples of callbacks are shown below. The code continues from
the two lines above.

.. code-block:: python

	# submit market buy for 20 shares of AAPL
	# if the first letter of the news body is 'T'
	def buyApple(msg, order):
	    newsBody = msg["news"]["body"]
	    if len(newsBody) > 0 and newsBody[0] == 'T':
	        order.addBuy('AAPL', 20)

	# don't forget this line!
	t.onNews = buyApple

	######################################################
	# each time AAPL trade happens for $x, make bid
	# and ask at $x-0.02, $x+0.02, respectively
	def marketMake(msg, order):
	    for trade in msg["trades"]:
	        if trade["ticker"] == 'AAPL':
	            px = trade["price"]
	            order.addBuy('AAPL', 10, px - 0.02)
	            order.addSell('AAPL', 10, px + 0.02)
	t.onTrade = marketMake

Running TradersBot
--------------------------------------
After adding all callbacks, call `t.run()` to start trading. TradersBot
will then connect to the MangoCore server and call your specified
callbacks upon an event. After calling this function, you cannot add or
modify your callbacks.