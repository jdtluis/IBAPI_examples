from ibapi.client import EClient, MarketDataTypeEnum
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order_condition import Create, OrderCondition
from ibapi.order import *

import threading
import time
import signal

class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.contract_details = {}  # Contract details will be stored here using reqId as a dictionary key

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextorderId = orderId
        print('The next valid order id is: ', self.nextorderId)

    def orderStatus(self, orderId, status, filled, remaining, avgFullPrice, permId, parentId, lastFillPrice, clientId,
                    whyHeld, mktCapPrice):
        print('orderStatus - orderid:', orderId, 'status:', status, 'filled', filled, 'remaining', remaining,
              'lastFillPrice', lastFillPrice)

    def openOrder(self, orderId, contract, order, orderState):
        print('openOrder id:', orderId, contract.symbol, contract.secType, '@', contract.exchange, ':', order.action,
              order.orderType, order.totalQuantity, orderState.status)

    def execDetails(self, reqId, contract, execution):
        print('Order Executed: ', reqId, contract.symbol, contract.secType, contract.currency, execution.execId,
              execution.orderId, execution.shares, execution.lastLiquidity)

    def contractDetails(self, reqId: int, contractDetails):
        self.contract_details[reqId] = contractDetails

    def get_contract_details(self, reqId, contract):
        self.contract_details[reqId] = None
        self.reqContractDetails(reqId, contract)
        # Error checking loop - breaks from loop once contract details are obtained
        for i in range(50):
            if not self.contract_details[reqId]:
                time.sleep(0.1)
            else:
                break
        # Raise if error checking loop count maxed out (contract details not obtained)
        if i == 49:
            raise Exception('error getting contract details')
        # Return contract details otherwise
        return app.contract_details[reqId].contract

    def tickPrice(self, reqId, tickType, price, attrib):
        if (tickType == 66 or tickType == 1) and reqId == 2:  #  66= Delayed BID, 1 = bid
            print('The current bid price is: ', price)
            try:
                # self.cancelOrder(self.nextorderId)
                #print('order id ' + order.orderId.__str__())
                order.lmtPrice = price + spread
                self.placeOrder(order.orderId, buy_contract, order)
            except:
                pass
        if (tickType == 67 or tickType == 2) and reqId == 1:   # 67 Delayed ask, 2 = ask
            print('The current ask price is: ', price)
            try:
                # self.cancelOrder(self.nextorderId)
                #print('order_sell id ' + order_sell.orderId.__str__())
                order_sell.lmtPrice = price - spread
                self.placeOrder(order_sell.orderId, sell_contract, order_sell)
            except:
                pass


def run_loop():
    app.run()


def Stock_contract(symbol, secType='STK', exchange='SMART', currency='USD', contractMonth=None):
    ''' custom function to create stock contract '''
    contract = Contract()
    contract.symbol = symbol
    contract.secType = secType
    contract.exchange = exchange
    contract.currency = currency
    if contractMonth:
        contract.lastTradeDateOrContractMonth = contractMonth # "202310"
    return contract


app = IBapi()
app.connect('127.0.0.1', 7497, 100)

app.nextorderId = None

# Start the socket in a thread
api_thread = threading.Thread(target=run_loop, daemon=True)
api_thread.start()

# Check if the API is connected via orderid
while True:
    if isinstance(app.nextorderId, int):
        print('connected')
        break
    else:
        print('waiting for connection')
        time.sleep(1)

# Create contracts
buy_contract = Stock_contract('MGC', secType='FUT', exchange='COMEX', contractMonth="202310") #Stock_contract('AAPL') #
sell_contract = Stock_contract('MGC', secType='FUT', exchange='COMEX', contractMonth="202312") # Stock_contract('AMZN')
spread =  -24 # buy - sell
buy_limit =  '1927' #'178'
buy_qty = 10
sell_limit =  '1949' #'134'
sell_qty = 10
# Update contract ID
# google_contract = app.get_contract_details(101, google_contract)

# Create order object
order = Order()
order.action = 'BUY'
order.totalQuantity = buy_qty
order.orderType = 'LMT'  # 'MKT'
order.lmtPrice = buy_limit  # - optional - you can add a buy stop limit here
# order.conditions.append(priceCondition)
order.orderId = app.nextorderId
order.transmit = True
order.eTradeOnly = False
order.firmQuoteOnly = False

order_sell = Order()
order_sell.action = 'SELL'
order_sell.totalQuantity = sell_qty
order_sell.orderType = 'LMT'  # 'MKT'
order_sell.lmtPrice = sell_limit  # - optional - you can add a buy stop limit here
# order.conditions.append(priceCondition)
order_sell.orderId = app.nextorderId + 1
order_sell.transmit = True
order_sell.eTradeOnly = False
order_sell.firmQuoteOnly = False


app.placeOrder(app.nextorderId, buy_contract, order)
app.placeOrder(app.nextorderId + 1, sell_contract, order_sell)

app.reqMarketDataType(MarketDataTypeEnum.DELAYED)
app.reqMktData(1, buy_contract, '', False, False, [])
time.sleep(.5)
app.reqMktData(2, sell_contract, '', False, False, [])


def signal_handler(sig, frame):
    app.cancelOrder(order.orderId)
    app.cancelOrder(order_sell.orderId)
    app.disconnect()


# Handler of Ctrl+C Event
signal.signal(signal.SIGINT, signal_handler)


while 1:
    time.sleep(1)
