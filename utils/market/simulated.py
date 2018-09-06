import copy
import datetime
import logging
import random

from upstox_api.api import OHLCInterval, LiveFeedType

from base import BaseMarket
from utils.loom import Loom


class SimMarket(BaseMarket):
    def __init__(self):
        super(SimMarket, self).__init__()
        self.counter = 0
        self.stockData = {}
        self._dummyMessages = {}

    def _isMarketOpen(self):
        if self.counter < 1:
            self.counter += 1
            return True
        else:
            return False

    def setSimDuration(self, startDate, days=1):
        assert isinstance(startDate, datetime.datetime), "Simulation start date must be a datetime object"
        assert isinstance(days, int), "Simulation end date must be an integer"
        self.startDate = startDate
        self.days = days

    def registerQuoteUpdate(self, traderName, instrument, callback, type=LiveFeedType.LTP):
        super(SimMarket, self).registerQuoteUpdate(traderName, instrument, callback)
        message = self.upstoxApi.get_live_feed(instrument, type)
        message['instrument'] = instrument
        self._dummyMessages[instrument.symbol] = message
        logging.debug("Captured dummy message for symbol %s" % instrument.symbol)

    def runSimulation(self):
        logging.info("Starting trading simulation")
        for date in (self.startDate + datetime.timedelta(days=n) for n in range(self.days)):
            self._simulateDay(date)
        logging.info("Simulation over.")

    def _simulateDay(self, date):
        logging.info("Starting simulation for day: %s" % (date.strftime("%d/%m/%y")))
        stockData = {}
        date = date.replace(hour=9, minute=15, second=0, microsecond=0)  # market open time
        for stock in self._subscribed:
            stockData[stock.symbol] = self.upstoxApi.get_ohlc(stock, OHLCInterval.Minute_1, date,
                                                              date.replace(hour=18, minute=00, second=0))
            if not len(stockData[stock.symbol]) == 375:
                logging.warning("Missing stock data for %s on %s" % (stock.symbol, date.strftime("%d/%m/%y")))
                return
            dayData = []
            yesterday = date.replace(hour=0, minute=0, second=0) - datetime.timedelta(days=1)
            while not dayData:
                dayData = self.upstoxApi.get_ohlc(stock, OHLCInterval.Day_1, yesterday,
                                                  yesterday + datetime.timedelta(days=1))
                yesterday = yesterday - datetime.timedelta(days=1)
            self._dummyMessages[stock.symbol]['close'] = dayData[0]['close']
            self._dummyMessages[stock.symbol]['open'] = stockData[stock.symbol][0]['open']
            logging.debug("Pulled OHLC data for symbol %s on date %s" % (stock.symbol, date.strftime("%d/%m/%y")))
        baseTimeStamp = int(date.strftime("%s")) * 1000
        for minute in range(0, 375):
            baseTimeStamp = baseTimeStamp + 60000
            openMessages = []
            closeMessages = []
            midMessages = []
            # TODO: Verify
            for symbol in stockData:
                message = copy.deepcopy(self._dummyMessages[symbol])
                message['ltp'] = stockData[symbol][minute]['open']
                openMessages.append(message)

                message = copy.deepcopy(self._dummyMessages[symbol])
                message['ltp'] = stockData[symbol][minute]['cp']
                closeMessages.append(message)

                message = copy.deepcopy(self._dummyMessages[symbol])
                message['ltp'] = stockData[symbol][minute]['high']
                midMessages.append(message)

                message = copy.deepcopy(self._dummyMessages[symbol])
                message['ltp'] = stockData[symbol][minute]['low']
                midMessages.append(message)

                for i in range(0, 4):
                    message = copy.deepcopy(self._dummyMessages[symbol])
                    message['ltp'] = round(
                        random.uniform(stockData[symbol][minute]['low'], stockData[symbol][minute]['high']), 2)
                    midMessages.append(message)
            random.shuffle(openMessages)
            random.shuffle(midMessages)
            random.shuffle(closeMessages)
            increment = 60000 / len(midMessages)
            for message in openMessages:
                message['timestamp'] = baseTimeStamp
                self._quoteUpdate(message)
            for index, message in enumerate(midMessages):
                message['timestamp'] = baseTimeStamp + (index * increment)
                self._quoteUpdate(message)
            for message in closeMessages:
                message['timestamp'] = baseTimeStamp + 60000
                self._quoteUpdate(message)
        Loom.waitForLoom()

    # TODO:
    # create update message template from one query for full update.
    # populate with OHLC Minute data + randomized data and return to all traders.
    """
    Sample:
    ltp = last traded price
    timestamp = ltt (last trade timestamp)
    open = open of session
    high = high so far
    low = low so far
    close = yesterday's close
    vtt = volume traded today
    atp = average trading price
    
    {'asks': [{'price': 0.0, 'orders': 0, 'quantity': 0}, 
    {'price': 0.0, 'orders': 0, 'quantity': 0},{'price': 0.0, 'orders': 0, 'quantity': 0}, 
    {'price': 0.0, 'orders': 0, 'quantity': 0},{'price': 0.0, 'orders': 0, 'quantity': 0}], 
    'ltp': 1548.2, 'spot_price': 0.0, 'total_sell_qty': 0, 'oi': None, 'exchange': u'NSE_EQ', 'timestamp': u'1536143236000', 
    'symbol': u'ACC', 'yearly_low': 1255.65, 
    'bids': [{'price': 1548.2, 'orders': 12, 'quantity': 4291}, {'price': 0.0, 'orders': 0, 'quantity': 0}, 
    {'price': 0.0, 'orders': 0, 'quantity': 0}, {'price': 0.0, 'orders': 0, 'quantity': 0}, {'price': 0.0, 'orders': 0, 'quantity': 0}], 
    'instrument': Instrument(exchange=u'NSE_EQ', token=22, parent_token=None, symbol=u'acc', name=u'ACC LIMITED', closing_price=1588.35, 
    expiry=None, strike_price=None, tick_size=5.0, lot_size=1, instrument_type=u'EQUITY', isin=u'INE012A01025'), 'ltt': 1536143235000, 
    'high': 1595.0, 'lower_circuit': 1429.55, 'low': 1521.65, 'atp': 1551.2, 'total_buy_qty': 4291, 'close': 1588.35, 
    'open': 1582.5, 'upper_circuit': 1747.15, 'vtt': 810463.0}
    """
    # def startDay(self):
    #     for symbol in self._subscribed:
    #         for data in self.stockData[symbol]:
    #             print('WIP')
