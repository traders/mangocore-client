Welcome to TradersBot
======================================
Welcome to TradersBot's documentation. TradersBot is a wrapper around the MangoCore API. It is provided by Traders@MIT to simplify the creation of algorithmic trading bots and price crawlers.

Why use TradersBot?
**************************************
Programs can crawl prices, put them into models, and submit trades far faster than any human can. Taking advantage of MangoCore's API will allow you to respond much faster to the market and make more money. This package is a Python wrapper for MangoCore's underlying JSON/websocket API, saving you the time from writing boilerplate code.

What to use TradersBot For
**************************************
This package is intended to be used with MangoCore at Traders@MIT competitions. If you do not know what these are, then this package will not be useful.

The foreign exchange case is the only one where you are allowed to submit buys and sells through the API. So, unless the code you're writing is for the FX case, you should never be interacting with :ref:`TradersOrder` objects.

In all cases, the API can be used passively, to only receive updates from MangoCore (but not send anything back). Whatever pricing model you come up with, you can write a script to pull prices, put them in the model, and assist you with click-trading.

Contents:
**************************************
.. toctree::
   :maxdepth: 2
   
   install
   bot
   order