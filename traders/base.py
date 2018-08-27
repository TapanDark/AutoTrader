from abc import ABCMeta, abstractmethod


class BaseTrader(object):
    __metaclass__ = ABCMeta

    def __init__(self, market):
        self.market = market
        self.interestedStocks = self._getInterestedStocks()
        # for stock in self.interestedStocks:
        #     self.market.

    @abstractmethod
    def _getInterestedStocks(self):
        return []

    @abstractmethod
    def stockUpdate(self, message):
        pass
