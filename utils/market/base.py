import datetime
import logging
import time
from abc import ABCMeta, abstractmethod
from collections import defaultdict

from upstox_api.api import *

from utils.api_helper import UpstoxHelper
from utils.loom import Loom
from utils.misc import automatedLogin


# MARKET_START = datetime.time(9, 15)
# MARKET_END = datetime.time(15, 30)


class BaseMarket(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, contracts=['NSE_EQ']):
        logging.debug("init %s" % self.__class__.__name__)
        self.contracts = contracts
        self.upstoxApi = None
        self._masterContractsByToken = {}
        self._symbols = {}
        self._APIConnect()
        self._registerCallBacks()
        self.upstoxApi.start_websocket(True)
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
            self._masterContractsByToken.update(self.upstoxApi.get_master_contract(contract))
        for token, instrument in self._masterContractsByToken.iteritems():
            self._symbols[instrument.symbol] = instrument

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
        logging.critical("Received trade update. RAW:\n%s" % message)
        # Loom.queueTask(callback,message)

    def _orderUpdate(self, message):
        # TODO: This method is not complete
        logging.critical("Received order update. RAW:\n%s" % message)
        # Loom.queueTask(callback,message)

    def getInstrument(self, symbol, market='NSE_EQ'):
        return self.upstoxApi.getInstrument(symbol, market)

    def getLastValue(self, instrument, type='full'):
        self.upstoxApi.get_live_feed(instrument, type)

    def registerQuoteUpdate(self, traderName, instrument, callback, type=LiveFeedType.LTP):
        # type = LiveFeedType.Full if feedType.lower() == 'full' else LiveFeedType.LTP if feedType.lower() == 'ltp' else None
        # assert type, "feedType must be 'full' or 'ltp'. Received %s" % feedType
        logging.debug("Registering TRADER:%s for SYMBOL:%s" % (traderName, instrument))
        if instrument not in self._subscribed:
            logging.debug("Subscribing instrument %s" % str(instrument))
            response = self.upstoxApi.subscribe(instrument, type)
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
        while self._isMarketOpen():
            time.sleep(60)
        logging.info("Market has closed. Trading day over")
        for traderId in self.traders:
            self.traders[traderId]['traderObj'].close()

    def placeOrder(self, symbol, quantity, price, transaction="buy", type="limit", product="delivery",
                   duration="day", trigger=None, stopLoss=None, squareOff=None, trailing=None, disclosed=0):
        if symbol.lower() not in self._symbols:
            logging.error("Uknown symbol %s." % symbol)
            return False
        if transaction.lower() not in ["buy", "sell"]:
            logging.error("Only buy/sell orders are supported")
            return False
        else:
            transaction = getattr(TransactionType, transaction.title())
        if not isinstance(quantity, int):
            logging.error("Order quantity must be an integer")
            return False
        if not isinstance(price, float) and not isinstance(price, int):
            logging.error("Order price must be a float or int")
            return False
        if type.lower() not in ["limit", "market"]:
            logging.error("Order Type must be Limit or Market")
            return False
        else:
            type = getattr(OrderType, type.title())
        if product.lower() not in ["delivery", "intraday"]:
            logging.error("Product must be of type deliver/intraday")
            return False
        else:
            product = getattr(ProductType,product.title())
        if duration not in ["day", "ioc"]:
            logging.error("Duration must be day or ioc")
            return False
        else:
            duration = getattr(DurationType, duration.upper())
        if trigger and not isinstance(trigger, float):
            logging.error("Trigger price must be a float")
            return False
        if stopLoss and not isinstance(stopLoss, float):
            logging.error("Stoploss must be a float")
            return False
        if squareOff and not isinstance(squareOff, float):
            logging.error("SquareOff must be a float")
            return False
        if trailing and not isinstance(trailing, float):
            logging.error("Trailing must be a float")
            return False
        if not isinstance(disclosed, int):
            logging.error("Disclosed must be an int")
            return False
        response = self.upstoxApi.place_order(transaction, self._symbols[symbol.lower()], quantity=quantity,
                                              order_type=type,
                                              product_type=product, price=price, trigger_price=trigger,
                                              disclosed_quantity=disclosed, duration=duration, stop_loss=stopLoss,
                                              square_off=squareOff, trailing_ticks=trailing)
        logging.info(response)
        return response
