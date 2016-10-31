import json
import tornado.ioloop, tornado.websocket
from tornado import gen
import traceback

class TradersBot:
	# takes in variable number of args
	def __doNothing(self, *args):
		pass

	def __init__(self, host, id, password, token = None):
		'''
		hyuh
		'''
		self.host = host
		self.id = id
		self.password = password
		self.token = token

		self.onAckRegister		= self.__doNothing
		"""MangoCore has acknowledged your registration. Callback function should be in form
		`f(msg, TradersOrder)` where msg is in the following format:

		.. code-block:: python

			{
			    "message_type": "ACK REGISTER",
			    "case_meta": {
			        "case_length": 300,
			        "securities": {
			            "AAPL": {
			                "tradeable": True,
			                "starting_price": 100,
			                "underlyings": {
			                    "AAPL": 1
			                }
			            },
			            # and so on...one per security
			        },
			        "underlyings": {
			            "AAPL": {
			                "name": "AAPL",
			                "limit": 1000
			            },
			            # and so on...one per security
			        }
			    },
			    "end_time": "0001-01-01T00:00:00Z",
			    "market_states": {
			        "AAPL": {
			            "ticker": "AAPL",
			            "bids": {},
			            "asks": {},
			            "last_price": 100,
			            "time":  "2015-03-21T20:54:05.530846913Z"
			        },
			        # and so on...one per security
			    },
			    "trader_state": {
			        "cash": {"USD": 100000}
			        # ... 
			        # this trader_state identical to one in onTraderUpdate
			        # see there for full details of this object
			    
			    },
			    # this token will match the one passed into TradersBot constructor
			    "token": "aylmao"
			}

		"""  
		self.onMarketUpdate		= self.__doNothing
		"""An update with the orderbook and last transaction price of some single ticker has arrived.
		This update will arrive roughly every half-second, as opposed to every time some event has changed
		the orderbook. But, you can still keep track of the orderbook at all times by listening to
		onTrade, which you do receive all of, and updating the orderbook accordingly. Callback function
		should be in form `f(msg, TradersOrder)` where `msg` is in the following format:

		.. code-block:: python

			{
			    "message_type": "MARKET UPDATE",
			    "market_state": {
			        "ticker": "AAPL",
			        "bids": {
			            "99.86": 350,
			            "99.87": 350,
			            "99.88": 300,
			            "99.89": 300,
			            "99.90": 300,
			            "99.91": 99,
			            "99.92": 170
			        },
			        "asks": {
			            "100.07": 133,
			            "100.08": 200,
			            "100.09": 250,
			            "100.10": 300,
			            "100.11": 300,
			            "100.13": 350,
			            "100.14": 350
			        },
			        "last_price": 100.07,
			        "time":  "2015-03-21T21:12:17.764384883Z"
			    }
			}

		"""
		self.onTraderUpdate		= self.__doNothing
		"""A periodic update with your current trade state (positions, PNL, open orders, ...) has arrived.
		This update will also only arrive roughly every half-second, but you should be internally keeping
		track of your positions and cash anyways, so much of this information should already be known.
		Callback function should be in form `f(msg, TradersOrder)` where `msg` is in the following format:

		.. code-block:: python

			{
			    "message_type": "TRADER UPDATE",
			    "trader_state": {
			        "cash": {"USD": 100000},
			        "positions": {
			            "AAPL": 0,
			            "IBM": 0,
			            "IDX": 0
			        },
			        "open_orders": {},
			        "pnl": {"USD": 0},
			        "time": "2015-03-21T20:54:05.530826573Z",
			        "total_fees": 0,
			        "total_fines": 0,
			        "total_rebates": 0
			    }
			}

		"""
		self.onTrade			= self.__doNothing
		"""A trade (not necessarily involving you) has occurred. Callback function should be in form
		`f(msg, TradersOrder)` where `msg` is in the following format:
		
		.. code-block:: python

			{
			    "message_type": "TRADE",
			    "trades": [
			        {
			            "trade_id": "AAPL:12",
			            "ticker": "AAPL",
			            "buy_order_id": "AAPL:88",
			            "sell_order_id": "AAPL:48",
			            "quantity": 50,
			            "price": 100.07,
			            "buy": True,
			            "time":  "2015-03-21T21:12:17.764311405Z"
			        },
			        # more trade {...} of the same type
			    ]
			}

		"""
		self.onAckModifyOrders	= self.__doNothing
		"""MangoCore has acknowledged your sell/buy/cancel order. Callback function should be in form
		`f(msg, TradersOrder)` where `msg` is in the following format:

		.. code-block:: python

			{
			    "message_type": "ACK MODIFY ORDERS",
			    "cancels": {
			        "AAPL:8349": None
			    },
			    "orders": [
			        {
			            "order_id": "AAPL:900o",
			            "ticker": "AAPL",
			            "buy": True,
			            "quantity": 100,
			            "price": 99.74,
			            "token": "sqv6ajor"
			        },
			        # more order {...} of the same type
			    ],
			    "token": "ze12a9k9"
			}

		A cancel with a None value indicates a successful cancellation.
		"""
		self.onNews				= self.__doNothing
		"""A news event has arrived. Callback function should be in form
		`f(msg, TradersOrder)` where msg is in the following format:
		
		.. code-block:: python

			{
			    "message_type": "NEWS",
			    "news": {
			        "headline": "Apple releases new Macbook",
			        "source": "Ars Technica",
			        "body": "Today, Apple releases a new shiny laptop.",
			        "time": 235,
			        "price": 0
			    }
			}

		Where time is the number of ticks since the round started, and price is the amount you must pay
		per news item you receive from this source (currently irrelevant).
		"""
		self.onAckSubscribe		= self.__doNothing
		"""
		.. note::
			The 2016 competition won't require subscribing to news, so this callback won't be used.

		MangoCore has acknowledged your subscription to a news source.
		"""
		self.onTenderOffer		= self.__doNothing
		"""
		.. note::
			The 2016 competition won't involve tender offers, so this callback won't be used.
		
		There's a tender offer you can accept.
		"""
		self.onAckTenderOffer	= self.__doNothing
		"""
		.. note::
			The 2016 competition won't involve tender offers, so this callback won't be used.

		MangoCore has acknowledged your tender offer order.
		"""
		self.onPing				= self.__doNothing
		"""
		.. note::
			MangoCore sends ping messages just to keep WebSocket connections alive. This probably
			isn't something that's useful to listen for.

		MangoCore sent the client a ping message. Callback function should be in the form
		`f(msg, TradersOrder)` where `msg` is the following:

		.. code-block:: python

			{ "message_type": "PING" }

		"""

		self.__periodics = []

	# Reads input from from the server and processes
	# them accordingly
	def __handle_read(self, msg):
		if msg is None:
			return
		msg = json.loads(msg)
		func = self.fmap.get(msg['message_type'])
		if func is not None:
			order = TradersOrder()
			try:
				func(msg, order)
			except Exception as e:
				traceback.print_exc()
				tornado.ioloop.IOLoop.instance().stop()
			order.toJson()
			for j in order.jsons:
				self.__write(j)

	def __write(self, msg):
		self.ws.write_message(msg)

	@gen.coroutine
	def __connect(self):
		self.ws = yield tornado.websocket.websocket_connect('ws://%s:10914/%s/%s' %
			(self.host, self.id, self.password), on_message_callback = self.__handle_read)
		if self.token is not None:
			self.__write(json.dumps({'message_type' : 'REGISTER', 'token' : self.token}))
		else:
			self.__write(json.dumps({'message_type' : 'REGISTER'}))
	def run(self):
		'''
		Starts the TradersBot. After this point, you can't add or modify any callbacks of
		the TradersBot.
		'''
		self.fmap = {
			'ACK REGISTER'		: self.onAckRegister,
			'PING'				: self.onPing,
			'MARKET UPDATE'		: self.onMarketUpdate,
			'TRADER UPDATE'		: self.onTraderUpdate,
			'TRADE'				: self.onTrade,
			'ACK MODIFY ORDERS'	: self.onAckModifyOrders,
			'NEWS'				: self.onNews,
			'ACK SUBSCRIBE'		: self.onAckSubscribe,
			'TENDER OFFER'		: self.onTenderOffer,
			'ACK TENDER OFFER'	: self.onAckTenderOffer
		}
		self.__connect()
		tornado.ioloop.PeriodicCallback(lambda : None, 1000).start()
		for p in self.__periodics:
			tornado.ioloop.PeriodicCallback(p[0], p[1]).start()
		tornado.ioloop.IOLoop.instance().start()

	def addPeriodicCallback(self, func, periodMs):
		'''
		.. warning::
			This function only exists because it's used in MangoCore stress tests to make sure
			MangoCore remains performant under periods of high frequency trade. We strongly advise
			against using this function in your trading code. Trades should happen in reaction to
			market events, which is what callbacks are for.

		Every `periodMs` milliseconds, TradersBot will call `func` with a blank TradersOrder.
		`func` should take in one parameter, a `TradersOrder`, that allows `func` to place orders.
		'''
		def f():
			order = TradersOrder()
			func(order)
			order.toJson()
			for j in order.jsons:
				self.__write(j)
		self.__periodics.append((f, periodMs))

class TradersOrder:
	def __init__(self):
		self.orders = []
		self.cancels = []
		self.jsons = []

	def addBuy(self, ticker, quantity, price = None, token = None):
		'''
		Add a buy order for `ticker`, of size `quantity` shares. If no price is passed in,
		the buy is taken as a market order. If `quantity` is negative, it is interpreted as a
		sell order of the positive amount. See :ref:`tokens` for the token parameter.
		'''
		self.addTrade(ticker, True, quantity, price, token)
	def addSell(self, ticker, quantity, price = None, token = None):
		'''
		Add a sell order for `ticker`, of size `quantity` shares. If no price is passed in,
		the sell is taken as a market order. If `quantity` is negative, it is interpreted as a
		buy order of the positive amount. See :ref:`tokens` for the token parameter.
		'''
		self.addTrade(ticker, False, quantity, price, token)

	def addTrade(self, ticker, isBuy, quantity, price = None, token = None):
		'''
		Submit an order for `ticker`, of size `quantity` shares. The order is a buy if `isBuy`
		is True and a sell otherwise. The order is a market order if no price is passed in.
		If `quantity` is negative, it is interpreted as an order of the opposite type, of the
		positive amount. See :ref:`tokens` for the token parameter.
		'''
		if quantity == 0:
			return
		if quantity < 0:
			quantity *= -1
			isBuy = not isBuy

		self.orders.append({"ticker":ticker, "buy":isBuy, "quantity":quantity})
		if price is not None:
			self.orders[-1]["price"] = price
		if token is not None:
			self.orders[-1]["token"] = token
	def addCancel(self, ticker, orderId):
		'''
		Cancel the order for `ticker` with the given `orderId`. The `orderId` is returned
		on `onAckModifyOrders`.
		'''
		self.cancels.append({"ticker":ticker, "order_id":orderId})

	def toJson(self, token = None):
		'''
		Turns a TradersOrder into a JSON string ready to be sent over to MangoCore. See :ref:`JSON`
		for the details of this format. By default, TradersBot will call this function for you with
		``token=None`` and then send the JSON to MangoCore, so there's no need to call it manually.
		However, there are two possible reasons to call it in your own code:

		#.	You want to specify a token for this set of orders, so you can keep track of them later.
			In this case, call ``toJson(token)`` at the end of your code, after you added all your
			buys, sells, and cancels.
		#.	You want to split your orders to be split up into multiple JSON messages. This scenario
			is highly unlikely; splitting up the orders will make you hit your rate limit faster,
			and offers no obvious benefits. Regardless, here is example code showing how to do so
			and the how the sent message differs from the usual:

			.. code-block:: python

				# When callback1 is called, MangoCore will receive 1 message
				# 1: {"message_type":"MODIFY ORDERS", "orders":[{"ticker":"AAPL","buy":true,"quantity":20},{"ticker":"GOOG","buy":false,"quantity":50}]}
				def callback1(msg, order):
					order.addBuy('AAPL', 20)
					order.addSell('GOOG', 50)

				# When callback2 is called, MangoCore will receive 2 messages
				# 1: {"message_type":"MODIFY ORDERS", "orders":[{"ticker":"AAPL","buy":true,"quantity":20}]}
				# 2: {"message_type":"MODIFY ORDERS", "orders":[{"ticker":"GOOG","buy":false,"quantity":50}], "token":"TOKEN123"}
				def callback2(msg, order):
					order.addBuy('AAPL', 20)
					order.toJson()
					order.addSell('GOOG', 50)
					order.toJson("TOKEN123")

		'''
		msgMap = {"message_type":"MODIFY ORDERS"}
		if len(self.orders) > 0:
			msgMap["orders"] = self.orders
		if len(self.cancels) > 0:
			msgMap["cancels"] = self.cancels
		if len(msgMap) > 1:
			# if we have more than just "message_type" key
			if token is not None:
				msgMap["token"] = token
			self.jsons.append(json.dumps(msgMap))
			self.orders = []
			self.cancels = []
