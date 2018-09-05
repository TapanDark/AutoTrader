from base import BaseTrader


class DummyTrader(BaseTrader):
    def __init__(self):
        super(DummyTrader, self).__init__()
        self.name = "DummyTrader"

    def _getInterestedStocks(self):
        return super(DummyTrader, self)._getInterestedStocks()

    def initialize(self, market):
        super(DummyTrader, self).initialize(market)

    def stockUpdate(self, message):
        super(DummyTrader, self).stockUpdate(message)
