import json
import zlib
import tornado.ioloop, tornado.websocket
from tornado import gen
import six

class TradersBot:
	# takes in variable number of args
	def __doNothing(self, *args):
		pass

	def __init__(self, host, id, password, token = None):
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

	# Reads input from from the server and processes
	# them accordingly
	def __handle_read(self, msg):
		if msg is None:
			return
		msg = zlib.decompress(msg, 16 + zlib.MAX_WBITS)
		msg = json.loads(msg.decode('utf-8'))
		func = self.fmap.get(msg['message_type'])
		if func is not None:
			res = func(msg)
			if res is not None:
				# if not a string, assume it is an object not JSON-ified yet
				if not isinstance(res, six.string_types):
					res = json.dumps(res)
				self.__write(res)

	def __write(self, msg):
		self.ws.write_message(msg)

	@gen.coroutine
	def __connect(self):
		self.ws = yield tornado.websocket.websocket_connect('ws://%s:10914/%s/%s' % 
			(self.host, self.id, self.password), on_message_callback = self.__handle_read)
		if self.token is not None:
			self.__write(json.dumps({'message_type' : 'REGISTER', 'token' : self.token}))
	def run(self):
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
		tornado.ioloop.IOLoop.instance().start()