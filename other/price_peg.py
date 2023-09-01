from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order_condition import Create, OrderCondition
from ibapi.order import *

import threading
import time


class IBapi(EWrapper, EClient):
	def __init__(self):
		EClient.__init__(self, self)
		self.contract_details = {} #Contract details will be stored here using reqId as a dictionary key

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

	def contractDetails(self, reqId: int, contractDetails):
		self.contract_details[reqId] = contractDetails

	def get_contract_details(self, reqId, contract):
		self.contract_details[reqId] = None
		self.reqContractDetails(reqId, contract)
		#Error checking loop - breaks from loop once contract details are obtained
		for i in range(50):
			if not self.contract_details[reqId]:
				time.sleep(0.1)
			else:
				break
		#Raise if error checking loop count maxed out (contract details not obtained)
		if i == 49:
			raise Exception('error getting contract details')
		#Return contract details otherwise
		return app.contract_details[reqId].contract

	def tickPrice(self, reqId, tickType, price, attrib):
		if tickType in (2, 67) and reqId == 1:
			print('The current ask price is: ', price)
			try:
				order.lmtPrice = price - offset
				self.placeOrder(self.nextorderId, contract_definition, order)
			except:
				pass


def run_loop():
	app.run()


def set_contract(symbol, secType='STK', exchange='SMART', currency='USD', contractMonth=None):
	contract = Contract()
	contract.symbol = symbol
	contract.secType = secType
	contract.exchange = exchange
	contract.currency = currency
	if contractMonth:
		contract.lastTradeDateOrContractMonth = contractMonth  # "202310"
	return contract

app = IBapi()
app.connect('127.0.0.1', 7497, 100)

app.nextorderId = None

#Start the socket in a thread
api_thread = threading.Thread(target=run_loop, daemon=True)
api_thread.start()

#Check if the API is connected via orderid
while True:
	if isinstance(app.nextorderId, int):
		print('connected')
		break
	else:
		print('waiting for connection')
		time.sleep(1)

#Create contracts
contract_definition = set_contract('AAPL', secType='STK', exchange='SMART', currency='USD', contractMonth=None)

offset = 0.5

#Create order object
order = Order()
order.action = 'BUY'
order.totalQuantity = 100
order.orderType = 'LMT'
order.lmtPrice = '187.5'
order.transmit = True
order.eTradeOnly = False
order.firmQuoteOnly = False

app.reqMarketDataType(3)  # Delayed data
app.reqMktData(1, contract_definition, '', False, False, [])

time.sleep(50)
app.cancelOrder(app.nextorderId)
app.disconnect()
