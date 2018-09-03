from abc import ABCMeta, abstractmethod

from upstox_api.api import LiveFeedType
from utils.misc import automatedLogin
from collections import defaultdict
from utils.api_helper import UpstoxHelper
import logging


class BaseMarket(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, upstoxObj, contracts=['NSE_EQ']):
        logging.debug("init %s" % self.__name__)
        self.upstoxApi = None
        self._APIConnect()
        self.masterContracts = self.upstoxApi.get_master_contract('NSE_EQ')
        self._registerCallBacks()
        self._subscribed = []
        self._quoteUpdateCallbacks = defaultdict(dict)

    def _registerCallBacks(self):
        self.upstoxApi.set_on_quote_update(self._quoteUpdate)
        self.upstoxApi.set_on_order_update(self._orderUpdate)
        self.upstoxApi.set_on_trade_update(self._tradeUpdate)

    def _APIConnect(self):
        self.upstoxApi = UpstoxHelper(UpstoxHelper.getApiKey())
        self.upstoxApi.authenticate(UpstoxHelper.getApiSecret(), UpstoxHelper.getRedirectUrl(), automatedLogin)
        self.upstoxApi.connect()

    @abstractmethod
    def _quoteUpdate(self, quote_object):
        logging.debug("Received quote update. RAW:\n%s" % quote_object)
        # update all traders who registered for this quote
        for (trader, callback) in self._quoteUpdateCallbacks[quote_object["instrument"].symbol]:
            logging.debug("Sending quote to TRADER:%s" % trader)
            callback(quote_object)
            # TODO : cache quote for providing day history

    def _tradeUpdate(self, message):
        # TODO: This method is not complete
        logging.debug("Received trade update. RAW:\n%s" % message)

    def _orderUpdate(self, message):
        # TODO: This method is not complete
        logging.debug("Received order update. RAW:\n%s" % message)

    @abstractmethod
    def getInstrument(self, symbol, market='NSQ_EQ'):
        self.upstoxApi.getInstrument(symbol, market)

    @abstractmethod
    def getLastValue(self, instrument, type='full'):
        self.upstoxApi.get_live_feed(instrument, type)

    @abstractmethod
    def registerQuoteUpdate(self, traderName, instrument, callback):
        # type = LiveFeedType.Full if feedType.lower() == 'full' else LiveFeedType.LTP if feedType.lower() == 'ltp' else None
        # assert type, "feedType must be 'full' or 'ltp'. Received %s" % feedType
        logging.debug("Registering TRADER:%s for SYMBOL:%s" % (traderName, instrument))
        if instrument not in self._subscribed:
            logging.debug("Subscribing instrument %s" % instrument)
            self.upstoxApi.subscribe(instrument, LiveFeedType.Full)
        self._quoteUpdateCallbacks[instrument.symbol] = (traderName, callback)
        logging.debug("Trader %s registerted for %s." % (traderName, instrument.symbol))

    # TODO: register interesting stocks for all traders, and dispatch events accordingly
    # TODO: Method stubs for all supported events, and methods for traders to register for them.
