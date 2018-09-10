from base import BaseMarket


class RealMarket(BaseMarket):
    def __init__(self, contracts=['NSE_EQ']):
        super(RealMarket, self).__init__(contracts=contracts)
