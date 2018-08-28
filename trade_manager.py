import logging
import argparse
import datetime

from utils.misc import automatedLogin
from utils.api_helper import UpstoxHelper, API_KEY, API_SECRET, REDIRECT_URL
from utils.tradeLogger import TradeLogger

apiKey = 'f8qMRApitW2Gkeymmq9kA9vSsp6W5S2U21OXkLk9'
accessToken = '7c0657e8ec714fe0bb7fbebbb1354b2b4f992857'


def storeCredentials():
    pass


def loadCredentials():
    pass


def getUpstoxHelper():
    logging.debug("Connecting to upstox api")
    upstoxApi = UpstoxHelper(API_KEY)
    upstoxApi.authenticate(API_SECRET, REDIRECT_URL, automatedLogin)
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

    except Exception as e:
        logging.exception("Exception ocurred!")
