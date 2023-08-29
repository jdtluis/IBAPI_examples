''' Demonstrates how to compute the moving average '''

from datetime import datetime
from threading import Thread
import time
import collections
import numpy as np

from ibapi.client import EClient, Contract, MarketDataTypeEnum
from ibapi.wrapper import EWrapper
from ibapi.utils import iswrapper

AVERAGE_LENGTH = 10


class Bollinger(EWrapper, EClient):
    ''' Serves as the client and the wrapper '''

    def __init__(self, addr, port, client_id):
        EClient.__init__(self, self)

        # Initialize members
        self.prices = collections.deque(maxlen=AVERAGE_LENGTH)
        self.avg_vals = []
        self.upper_band = []
        self.lower_band = []

        # Connect to TWS
        self.connect(addr, port, client_id)

        # Launch the client thread
        thread = Thread(target=self.run, daemon=True)
        thread.start()
        time.sleep(1)

    @iswrapper
    def tickPrice(self, reqId, tickType, price, attrib):
        if tickType in (1,2,66,67) and reqId == 1:
            print('Some prices: ', price.__str__())
            # Append the closing price to the deque
            self.prices.append(price)

            # Compute the average if 100 values are available
            if len(self.prices) == AVERAGE_LENGTH:
                avg = sum(self.prices) / len(self.prices)

                # Compute the standard deviation
                avg_array = np.array(self.prices)
                sigma = np.std(avg_array)

                # Update the containers
                self.avg_vals.append(avg)
                self.upper_band.append(avg + 2 * sigma)
                self.lower_band.append(avg - 2 * sigma)
        #else:
        #    print('TickType ', tickType.__str__())

    @iswrapper
    def tickSize(self, reqId, tickType, size):
        pass
        # if tickType == 2 and reqId == 1:
        #print(f'The current {reqId} and type {tickType} is: ', size.__str__(), tickType)

    # @iswrapper
    # def historicalDataEnd(self, reqId, start, end):
    #     print('Moving average: {}'.format(self.avg_vals))
    #     print('Upper band: {}'.format(self.upper_band))
    #     print('Lower band: {}'.format(self.lower_band))

    @iswrapper
    def error(self, reqId, code, msg):
        print('Error {}: {}'.format(code, msg))


def FUT_order(symbol, exchange='COMEX', futMonth="202310"):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = 'FUT'
    contract.exchange = exchange
    contract.currency = 'USD'
    contract.lastTradeDateOrContractMonth = futMonth
    return contract


def main(seconds, ip):
    # Create the client and connect to TWS
    client = Bollinger(ip, 7497, 0)

    # Define a contract for IBM stock
    contract = Contract()
    contract.symbol = "TSLA"
    contract.secType = "STK"
    contract.exchange = "SMART"
    contract.currency = "USD"

    client.reqMarketDataType(MarketDataTypeEnum.DELAYED)
    client.reqMktData(1, FUT_order('MGC', exchange='COMEX', futMonth="202310"), '', False, False, []) # FUT_order('MGC', exchange='COMEX', futMonth="202310")

    # Sleep while the request is processed
    time.sleep(seconds)

    # Disconnect from TWS
    client.disconnect()
    return client


if __name__ == '__main__':
    import sys
    secs = input('Seconds < 360')
    ip = input('Set IP adress')
    if not ip:
        ip = '127.0.0.1'
    try:
        if secs:
            secs = int(secs)
    except Exception as e:
        print(f'Error: {e}')
        secs = input('Segundos < 360')
    client = main(secs, ip)
