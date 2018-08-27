from abc import ABCMeta, abstractmethod
from utils.api_helper import UpstoxHelper, API_KEY, API_SECRET, REDIRECT_URL
from upstox_api.api import LiveFeedType
from utils.misc import automatedLogin
from collections import defaultdict
import logging


class BaseMarket(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, contracts=['NSE_EQ']):
        logging.debug("init %s" % self.__name__)
        self._APIConnect()
        self._registerCallBacks()
        self.masterContracts = self.upstoxApi.get_master_contract('NSE_EQ')
        self._subscribed = []
        self._quoteUpdateCallbacks = defaultdict(dict)

    def _APIConnect(self):
        logging.debug("Connecting to upstox api")
        self.upstoxApi = UpstoxHelper(API_KEY)
        self.upstoxApi.authenticate(API_SECRET, REDIRECT_URL, automatedLogin)
        self.upstoxApi.connect()
        logging.debug("Connection to api successful")

    def _registerCallBacks(self):
        pass

    @abstractmethod
    def _quoteUpdate(self, message):
        # TODO: This method is not complete
        logging.debug("Received quote update. RAW:\n%s" % message)
        for (trader, callback) in self._quoteUpdateCallbacks:
            logging.debug("Sending quote to TRADER:%s" % trader)
            callback(message)

    @abstractmethod
    def getInstrument(self, market, symbol):
        pass

    @abstractmethod
    def getLastValue(self, instrument, type='full'):
        pass

    @abstractmethod
    def registerQuoteUpdate(self, instrument, traderName, callback):
        # type = LiveFeedType.Full if feedType.lower() == 'full' else LiveFeedType.LTP if feedType.lower() == 'ltp' else None
        # assert type, "feedType must be 'full' or 'ltp'. Received %s" % feedType
        logging.debug("Registering TRADER:%s for SYMBOL:%s" % (traderName, instrument))
        if instrument not in self._subscribed:
            logging.debug("Subscribing instrument %s" % instrument)
            self.upstoxApi.subscribe(instrument, LiveFeedType.Full)
        # TODO: This method is not complete
        # self._quoteUpdateCallbacks[]
        logging.debug("Registration successful.")

    # TODO: register interesting stocks for all traders, and dispatch events accordingly
    # TODO: Method stubs for all supported events, and methods for traders to register for them.
