from base import BaseTrader
from collections import defaultdict, OrderedDict
import matplotlib.pyplot as plt


class DummyTrader(BaseTrader):
    def __init__(self):
        super(DummyTrader, self).__init__()
        self.name = "DummyTrader"
        self.stockData = defaultdict(list)

    def _getInterestedStocks(self):
        return super(DummyTrader, self)._getInterestedStocks()

    def initialize(self, market):
        super(DummyTrader, self).initialize(market)

    def stockUpdate(self, message):
        super(DummyTrader, self).stockUpdate(message)
        self.stockData[message['symbol']].append(message['ltp'])

    def close(self):
        import pdb
        pdb.set_trace()
        for symbol in self.stockData:
            plt.plot(self.stockData[symbol])
            plt.ylabel('Price')
            plt.xlabel('Timestamps')
            plt.show()