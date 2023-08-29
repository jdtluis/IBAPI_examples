from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract

import threading
import time


class IBapi(EWrapper, EClient):
	def __init__(self):
		EClient.__init__(self, self)
		
	def tickPrice(self, reqId, tickType, price, attrib):
		if (tickType == 67 or tickType == 2) and reqId in (2, 3):
			print(f'The current ask price for {reqId} is: ', price)
		else:
			pass
			#print(f'The current {reqId} and type {tickType} is: ', price.__str__())


def run_loop():
	app.run()

app = IBapi()
app.connect('127.0.0.1', 7497, 123)

#Start the socket in a thread
api_thread = threading.Thread(target=run_loop, daemon=True)
api_thread.start()

time.sleep(1) #Sleep interval to allow time for connection to server

#Create contract object
XAUUSD_contract = Contract() 
XAUUSD_contract.symbol = 'XAUUSD' 
XAUUSD_contract.secType = 'CMDTY' 
XAUUSD_contract.exchange = 'SMART' 
XAUUSD_contract.currency = 'USD'

#Request Market Data
app.reqMktData(1, XAUUSD_contract, '', False, False, [])

contract = Contract()
contract.symbol = "MGC"
contract.secType = "FUT"
contract.exchange = "COMEX"
contract.currency = "USD"
contract.lastTradeDateOrContractMonth = "202310"
app.reqMarketDataType(3)
app.reqMktData(2, contract, '', False, False, [])

contract = Contract()
contract.symbol = "MGC"
contract.secType = "FUT"
contract.exchange = "COMEX"
contract.currency = "USD"
contract.lastTradeDateOrContractMonth = "202312"
app.reqMktData(3, contract, '', False, False, [])


time.sleep(10) #Sleep interval to allow time for incoming price data
app.disconnect()
