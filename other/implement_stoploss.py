from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import *

import threading
import time


class IBapi(EWrapper, EClient):
	
	def __init__(self):
		EClient.__init__(self, self)
	
	def nextValidId(self, orderId: int):
		super().nextValidId(orderId)
		self.nextorderId = orderId
		print('The next valid order id is: ', self.nextorderId)

	def orderStatus(self, orderId, status, filled, remaining, avgFullPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
		print('orderStatus - orderid:', orderId, 'status:', status, 'filled', filled, 'remaining', remaining, 'lastFillPrice', lastFillPrice)
	
	def openOrder(self, orderId, contract, order, orderState):
		print('openOrder id:', orderId, contract.symbol, contract.secType, '@', contract.exchange, ':', order.action, order.orderType, order.totalQuantity, orderState.status)

	def execDetails(self, reqId, contract, execution):
		print('Order Executed: ', reqId, contract.symbol, contract.secType, contract.currency, execution.execId, execution.orderId, execution.shares, execution.lastLiquidity)


def run_loop():
	app.run()


def FX_order(symbol):
	contract = Contract()
	contract.symbol = symbol[:3]
	contract.secType = 'CASH'
	contract.exchange = 'IDEALPRO'
	contract.currency = symbol[3:]
	return contract


def FUT_order(symbol, exchange='COMEX', futMonth="202310"):
	contract = Contract()
	contract.symbol = symbol
	contract.secType = 'FUT'
	contract.exchange = exchange
	contract.currency = 'USD'
	contract.lastTradeDateOrContractMonth = futMonth
	return contract


app = IBapi()
app.connect('127.0.0.1', 7497, 123)

app.nextorderId = None

#Start the socket in a thread
api_thread = threading.Thread(target=run_loop, daemon=True)
api_thread.start()

#Check if the API is connected via orderid
while True:
	if isinstance(app.nextorderId, int):
		print('connected')
		print()
		break
	else:
		print('waiting for connection')
		time.sleep(1)

#Create order object
order = Order()
order.action = 'BUY'
order.orderType = 'LMT'
order.orderId = app.nextorderId
app.nextorderId += 1
order.transmit = False
order.eTradeOnly = False
order.firmQuoteOnly = False

#Create stop loss order object
stop_order = Order()
stop_order.action = 'SELL'
stop_order.orderType = 'STP'
stop_order.orderId = app.nextorderId
app.nextorderId += 1
stop_order.parentId = order.orderId
stop_order.transmit = True
stop_order.eTradeOnly = False
stop_order.firmQuoteOnly = False


if __name__ == '__main__':
	# Place orders
	order.lmtPrice = '1928.5'
	order.totalQuantity = 10
	stop_order.auxPrice = '1927'
	stop_order.totalQuantity = 10
	app.placeOrder(order.orderId, FUT_order('MGC', exchange='COMEX', futMonth="202310"), order)
	app.placeOrder(stop_order.orderId, FUT_order('MGC', exchange='COMEX', futMonth="202310"), stop_order)
	#app.placeOrder(order.orderId, FX_order('EURUSD'), order)
	#app.placeOrder(stop_order.orderId, FX_order('EURUSD'), stop_order)
	time.sleep(50)
	# Cancel order
	print()
	print('cancelling order')
	app.cancelOrder(order.orderId)
	time.sleep(3)
	app.disconnect()
