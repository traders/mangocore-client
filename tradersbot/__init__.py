import json
import zlib
import tornado.ioloop, tornado.websocket
from tornado import gen

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
		self.onPing				= self.__doNothing
		self.onMarketUpdate		= self.__doNothing
		self.onTraderUpdate		= self.__doNothing
		self.onTrade			= self.__doNothing
		self.onAckModifyOrders	= self.__doNothing
		self.onNews				= self.__doNothing
		self.onAckSubscribe		= self.__doNothing
		self.onTenderOffer		= self.__doNothing
		self.onAckTenderOffer	= self.__doNothing

		self.__periodics = []

	# Reads input from from the server and processes
	# them accordingly
	def __handle_read(self, msg):
		if msg is None:
			return
		msg = zlib.decompress(msg, 16 + zlib.MAX_WBITS)
		msg = json.loads(msg.decode('utf-8'))
		func = self.fmap.get(msg['message_type'])
		if func is not None:
			order = TradersOrder()
			func(msg, order)
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
		hyuh
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
			This function only exists because it used in MangoCore stress tests, to make sure
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
