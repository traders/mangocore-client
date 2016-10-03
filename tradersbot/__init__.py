import json
import zlib
import tornado.ioloop, tornado.websocket
from tornado import gen

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
		#print msg
		type = msg['message_type']
		res = None
		if type == 'ACK REGISTER':
			res = self.onAckRegister(msg)
		elif type == 'PING':
			res = self.onPing(msg)
		elif type == 'MARKET UPDATE':
			res = self.onMarketUpdate(msg)
		elif type == 'TRADER UPDATE':
			res = self.onTraderUpdate(msg)
		elif type == 'TRADE':
			res = self.onTrade(msg)
		elif type == 'ACK MODIFY ORDERS':
			res = self.onAckModifyOrders(msg)
		elif type == 'NEWS':
			res = self.onNews(msg)
		elif type == 'ACK SUBSCRIBE':
			res = self.onAckSubscribe(msg)
		elif type == 'TENDER OFFER':
			res = self.onTenderOffer(msg)
		elif type == 'ACK TENDER OFFER':
			res = self.onAckTenderOffer(msg)
		if res is not None:
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
		self.__connect()
		tornado.ioloop.PeriodicCallback(lambda : None, 1000).start()
		tornado.ioloop.IOLoop.instance().start()