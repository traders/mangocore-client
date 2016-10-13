# TradersBot
Python wrapper for MangoCore API; used for Traders@MIT algorithmic trading cases. Compatible with Python 2.7/3.
### Installation
Install Python and pip if needed. Find the appropriate Python installer [here](https://www.python.org/downloads/); type in the terminal `easy_install pip` to get pip.
Then type 

    pip install tradersbot
    
to install the `tradersbot` package.

### Usage
Import `tradersbot` and instantiate a TradersBot; the constructor takes in the mangocore server IP/URL, a username, a password, and an optional token:

    from tradersbot import TradersBot
    import json # needed to send json messages later
    t = TradersBot('18.247.12.164', 'MIT2', 'password')

Next, for each MangoCore message that you want to listen to, specify a function to be called on the receipt of the message. The messages you can subscribe to are:
- onAckRegister
- onPing
- onMarketUpdate
- onTraderUpdate
- onTrade
- onAckModifyOrders
- onNews
- onAckSubscribe
- onTenderOffer
- onAckTenderOffer

Each of these functions should take in one argument, a map that contains all information from that message. Read the case packet for more information on what information is contained in each message type. For example:

    def onNews(msg):
        return json.dumps({'message_type' : 'MODIFY ORDERS', 'orders' : [{'ticker' : 'AAPL', 'buy' : True, 'quantity' : 5}]})
    t.onNews = onNews

Will buy 5 AAPL shares each time a news event is received. You can also return the dictionary directly; `TradersBot` assumes that if your function returns an object that isn't a string, it is an object that `TradersBot` needs to json-ify before sending. So the following also works:

    def onNews(msg):
        return {'message_type' : 'MODIFY ORDERS', 'orders' : [{'ticker' : 'AAPL', 'buy' : True, 'quantity' : 5}]}
    t.onNews = onNews

Finally, run the bot:

    t.run()
	
Note that after this function is called, you can't change the event listener functions; for example, you can't add a handler to `onPing` halfway through trading.
