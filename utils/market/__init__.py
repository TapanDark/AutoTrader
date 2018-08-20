from abc import ABCMeta, abstractmethod


class Market(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, contracts):
        pass

    @abstractmethod
    def getInstrument(self, market, symbol):
        pass

    @abstractmethod
    def getLastValue(self, instrument, type='full'):
        pass

    # TODO: register interesting stocks for all traders, and dispatch events accordinly
    # TODO: Method stubs for all supported events, and methods for traders to register for them.

    #
    # @abstractmethod
    # def register(self, ):
