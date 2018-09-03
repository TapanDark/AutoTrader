import logging
import argparse
import datetime

from utils.misc import automatedLogin
from utils.api_helper import UpstoxHelper
from utils.tradeLogger import TradeLogger
from utils.loom import Loom


def storeCredentials():
    pass


def loadCredentials():
    pass


def getUpstoxHelper():
    logging.debug("Connecting to upstox api")
    upstoxApi = UpstoxHelper(UpstoxHelper.getApiKey())
    upstoxApi.authenticate(UpstoxHelper.getApiSecret(), UpstoxHelper.getRedirectUrl(), automatedLogin)
    upstoxApi.connect()
    logging.debug("Connection to api successful")
    return upstoxApi


def parseArguments(parser):
    parser.add_argument("--simulation", default=True)
    parser.add_argument("--simDate", default=datetime.datetime.today() - datetime.timedelta(1))
    arguments = parser.parse_args()
    logging.debug("Arguments:%s" % arguments)


if __name__ == "__main__":
    try:
        TradeLogger.basicConfig()
        logging.debug("Parsing arguments")
        parser = argparse.ArgumentParser()
        parseArguments(parser)
        logging.info("Creating upstox helper object")
        upstoxHelper = getUpstoxHelper()
        Loom.waitForLoom()  # call in cleanup
    except Exception as e:
        logging.exception("Exception ocurred!")
