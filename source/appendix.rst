Appendix
======================================

.. _JSON:

Client-to-Server JSON Format
--------------------------------------
Registering
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: python

	{
	    "message_type": "REGISTER",
	    "token": "aylmao"
	}

Adding/Canceling Orders
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: python

	{
	    "message_type": "MODIFY ORDERS",
	    "orders": [
			{
	            "ticker": "AAPL",
	            "buy": True,
	            "quantity": 100,
	            "price": 99.74,
	            "token": "sqv6ajor"
	        },
	        # and so on...one map object for each buy/sell
	    ],
	    "cancels": [
	        {
	            "ticker": "AAPL",
	            "order_id": "AAPL:8779"
		    }
	        # and so on...one map object for each cancel
	    ],
	    "token": "ze12a9k9" # as always, is optional
	}

The orders and cancels fields are optional. If you are only sending
buys and sells, feel free to not even include the `cancels` key. If
you are only cancelling, then feel free to not include the `orders`
key.

Subscribing to News
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: python

	{
	    "message_type": "SUBSCRIBE NEWS",
	    "subscribes": ["The Wall Street Journal", "Bloomberg"]
	    "unsubscribes": ["New York Post"],
	    "token": "e23sle9w"
	}

The `subscribes` and `unsubscribes` lists may be omitted if they are
empty, similar to `orders` and `cancels` in ``MODIFY ORDERS``.

Accepting Tender Offers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: python

	{
	    "message_type": "ACCEPT TENDER OFFER",
	    "token": "oeoh6w29",
	    "tender_offer": {
	        "buy": False,
	        "offer_id": "AAPL:0",
	        "price": 100,
	        "quantity": 400,
	        "ticker": "AAPL",
	        "time": 10,
	        "time_remaining": 10
	    }
	}

.. _tokens:

Tokens
--------------------------------------
Tokens are MangoCore's way of uniquely tagging your messages. Any
message you send to MangoCore can optionally have a token parameter.
When MangoCore responds to your message (for example, it responds to
the ``MODIFY ORDERS`` message with an ``ACK MODIFY ORDERS`` message),
the response will include a token field whose value is equal to the
token you passed in. By this, we mean that if you send:

.. code-block:: python

	{
	    "message_type": "MODIFY ORDERS",
	    "cancels": [
	        {
	            "ticker": "AAPL",
	            "order_id": "AAPL:8149"
	        }
	    ],
	    "token": "kfnwxw29"
	}

MangoCore will respond with:

.. code-block:: python

	{
	    "message_type": "ACK MODIFY ORDERS",
	    "cancels": {
	        "AAPL:8149": None
	    },
	    "token": "kfnwxw29",
	    # see TradersBot page for message format
	}

where the token value in ``ACK TRADE`` is exactly same as the one
given in ``TRADE``. The token allows you to determine which ``TRADE``
message a given ``ACK TRADE`` is responding to if you sent multiple
``TRADE`` messages. This is very useful for identifying among the
potentially thousands of trade messages you send.

We go through each possible place where you can send a token. For
each, we give possible reasons why tokens might be useful in this
message, and what server-to-client messages would mention this token. 

1. ``REGISTER``

   **Referenced in:** ``ACK REGISTER``

   **Why:** Probably not useful. Tokens are ony allowed in ``REGISTER``
   messages for consistency with other client-to-server messages.
   Perhaps if you run multiple bots trading on the same account, each
   would register with a different token.

2. ``MODIFY ORDERS``

   **Referenced in:** ``ACK MODIFY ORDERS``

   **Why:** Tokens for the overall ``MODIFY ORDERS`` message are not
   very useful. But, you can make a map of token to ticker, quantity,
   price, and ``order_id`` which can help you keep track of your
   positions and ``order_id``'s in case you want to cancel anything.
   
3. ``SUBSCRIBE NEWS``

   **Referenced in:** ``ACK SUBSCRIBE``

   **Why:** Probably not useful.
   
4. ``ACCEPT TENDER OFFER``
   **Referenced in:** ``ACK TENDER OFFER``

   **Why:** Since ``offer_id`` in the tender offer message should
   already uniquely identify the tender offer, tokens probably
   aren't very useful in this situation.
