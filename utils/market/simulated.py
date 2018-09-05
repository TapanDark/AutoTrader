import datetime
import logging

from upstox_api.api import OHLCInterval

from base import BaseMarket


class SimMarket(BaseMarket):
    def __init__(self):
        super(SimMarket, self).__init__()
        self.counter = 0
        self.stockData = {}

    def _isMarketOpen(self):
        if self.counter < 1:
            self.counter += 1
            return True
        else:
            return False

    def setSimDate(self, date=None):
        if date:
            assert isinstance(date, datetime.datetime)
        else:
            date = datetime.datetime.now() - datetime.timedelta(days=1)
        self.date = date
        for stock in self._subscribed:
            self.stockData[stock.symbol] = self.upstoxApi.get_ohlc(stock, OHLCInterval.Minute_1, date,
                                                                   date + datetime.timedelta(days=1))
            assert len(self.stockData[stock.symbol]) == 750, "Missing stock data for %s on %s" % (
                stock.symbol, date.strftime("%d/%m/%y"))
            logging.info("Pulled OHLC data for symbol %s on date %s" % (stock.symbol, date.strftime("%d/%m/%y")))

    # TODO:
    # create update message template from one query for full update.
    # populate with OHLC Minute data + randomized data and return to all traders.
    """
    Sample:
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
