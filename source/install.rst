.. _install:

Installation and Example
======================================
Install Python and pip if needed. Find the appropriate Python installer `here <https://www.python.org/downloads/>`_; type in the terminal ``easy_install pip`` to get pip. Then type ``pip install tradersbot`` to install the tradersbot package.

Usage
**************************************
First, import the ``tradersbot`` package and instantiate a ``TradersBot``.

.. code-block:: python

	from tradersbot import TradersBot
	t = TradersBot('18.247.12.164', 'MIT2', 'password')

TradersBot is based on callbacks; for each message type MangoCore sends, you may specify a callback function which will be called whenever TradersBot receives a message of that type from MangoCore.