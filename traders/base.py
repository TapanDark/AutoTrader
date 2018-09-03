import logging
from abc import ABCMeta, abstractmethod


class BaseTrader(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.market = None
        self.name = "BASE_TRADER"

    @abstractmethod
    def initialize(self, market):
        assert self.name != "BASE_TRADER", "Trader name not set!"
        self.market = market
        for stock in self._getInterestedStocks():
            market.registerQuoteUpdate(self.name, stock, self.stockUpdate)

    @abstractmethod
    def _getInterestedStocks(self):
        return self.market.getInstrument("TATASTEEL")

    @abstractmethod
    def stockUpdate(self, message):
        logging.info("Trader %s has received quote update for stock %s" % (self.name, message['instrument'].symbol))
