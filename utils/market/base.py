import logging
import time
import datetime

from abc import ABCMeta, abstractmethod
from collections import defaultdict
from upstox_api.api import LiveFeedType
from utils.api_helper import UpstoxHelper
from utils.loom import Loom
from utils.misc import automatedLogin

MARKET_START = datetime.time(9, 15)
MARKET_END = datetime.time(15, 30)


class BaseMarket(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, contracts=['NSE_EQ']):
        logging.debug("init %s" % self.__class__.__name__)
        self.contracts = contracts
        self.upstoxApi = None
        self._APIConnect()
        self._registerCallBacks()
        self._subscribed = []
        self._quoteUpdateCallbacks = defaultdict(list)
        self.traders = {}

    def _registerCallBacks(self):
        self.upstoxApi.set_on_quote_update(self._quoteUpdate)
        self.upstoxApi.set_on_order_update(self._orderUpdate)
        self.upstoxApi.set_on_trade_update(self._tradeUpdate)

    def _APIConnect(self):
        self.upstoxApi = UpstoxHelper(UpstoxHelper.getApiKey())
        if getattr(UpstoxHelper, "accessToken", None):  # TODO: WAR, fix this. One connect call should handle all
            self.upstoxApi.accessToken = UpstoxHelper.accessToken
        else:
            self.upstoxApi.authenticate(UpstoxHelper.getApiSecret(), UpstoxHelper.getRedirectUrl(), automatedLogin)
        self.upstoxApi.connect()
        for contract in self.contracts:
            self.masterContracts = self.upstoxApi.get_master_contract(contract)

    def _quoteUpdate(self, quote_object):
        logging.debug("Received quote update. RAW:\n%s" % quote_object)
        # update all traders who registered for this quote
        for item in self._quoteUpdateCallbacks[quote_object["instrument"].symbol]:
            trader, callback = item
            logging.debug("Sending quote to TRADER:%s" % trader)
            Loom.pushTask(callback, quote_object)
        # TODO : cache quote for providing day history

    def _tradeUpdate(self, message):
        # TODO: This method is not complete
        logging.debug("Received trade update. RAW:\n%s" % message)
        # Loom.queueTask(callback,message)

    def _orderUpdate(self, message):
        # TODO: This method is not complete
        logging.debug("Received order update. RAW:\n%s" % message)
        # Loom.queueTask(callback,message)

    def getInstrument(self, symbol, market='NSE_EQ'):
        return self.upstoxApi.getInstrument(symbol, market)

    def getLastValue(self, instrument, type='full'):
        self.upstoxApi.get_live_feed(instrument, type)

    def registerQuoteUpdate(self, traderName, instrument, callback):
        # type = LiveFeedType.Full if feedType.lower() == 'full' else LiveFeedType.LTP if feedType.lower() == 'ltp' else None
        # assert type, "feedType must be 'full' or 'ltp'. Received %s" % feedType
        logging.debug("Registering TRADER:%s for SYMBOL:%s" % (traderName, instrument))
        if instrument not in self._subscribed:
            logging.debug("Subscribing instrument %s" % str(instrument))
            response = self.upstoxApi.subscribe(instrument, LiveFeedType.LTP)
            if not response["success"]:
                logging.error("Failed to subscribe to %s" % instrument)
                return False
            self._subscribed.append(instrument)
        self._quoteUpdateCallbacks[instrument.symbol].append((traderName, callback))
        logging.debug("Trader %s registerted for %s." % (traderName, instrument.symbol))
        return True

    def addTrader(self, traderObj, budget):
        logging.info(
            "Registering trader:%s in market:%s for margin : %s" % (traderObj.name, self.__class__.__name__, budget))
        traderID = id(traderObj)
        if traderID in self.traders:
            logging.warning("Trader %s already registered" % (traderObj.__class__.__name__))
        self.traders[traderID] = {
            "traderObj": traderObj,
            "margin": budget
        }
        traderObj.initialize(self)

    def _isMarketOpen(self):
        now = datetime.datetime.now()
        if not now.weekday() > 5:
            return False
        if now.time() > MARKET_START and now.time() < MARKET_END:
            return True
        return False

    def startDay(self):
        logging.info("Starting trading day")
        self.upstoxApi.start_websocket(True)
        while self._isMarketOpen():
            time.sleep(60)
        logging.info("Market has closed. Trading day over")
