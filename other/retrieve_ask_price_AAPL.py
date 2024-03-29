from ibapi.client import EClient,MarketDataTypeEnum
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract

import threading
import time


class IBapi(EWrapper, EClient):
	def __init__(self):
		EClient.__init__(self, self)

	def tickPrice(self, reqId, tickType, price, attrib):
		if tickType == 2 and reqId == 1:
			print('The current ask price is: ', price.__str__())
		elif tickType == 1 and reqId == 1:
			print('The current bid price is: ', price.__str__())

	def tickSize(self, reqId, tickType, size):
		#if tickType == 2 and reqId == 1:
		print(f'The current {reqId} and type {tickType} is: ', size.__str__(), tickType)

def run_loop():
	app.run()

app = IBapi()
app.connect('127.0.0.1', 7497, 58)

#Start the socket in a thread
api_thread = threading.Thread(target=run_loop, daemon=True)
api_thread.start()

time.sleep(1) #Sleep interval to allow time for connection to server

#Create contract object
apple_contract = Contract()
apple_contract.symbol = 'TSLA'
apple_contract.secType = 'STK'
apple_contract.exchange = 'SMART'
apple_contract.currency = 'USD'

#Request Market Data
app.reqMarketDataType(MarketDataTypeEnum.DELAYED)
app.reqMktData(1, apple_contract, '', False, False, [])

time.sleep(50) #Sleep interval to allow time for incoming price data
app.disconnect()
