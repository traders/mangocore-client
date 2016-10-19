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
		hyuh
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
		hyuh
		'''
		self.addTrade(ticker, True, quantity, price, token)
	def addSell(self, ticker, quantity, price = None, token = None):
		'''
		hyuh
		'''
		self.addTrade(ticker, False, quantity, price, token)

	def addTrade(self, ticker, isBuy, quantity, price = None, token = None):
		'''
		hyuh
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
		hyuh
		'''
		self.cancels.append({"ticker":ticker, "order_id":orderId})

	def toJson(self, token = None):
		'''
		hyuh
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
