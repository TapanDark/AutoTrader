import logging

from utils.api_helper import UpstoxHelper
from utils.automated_login import automatedLogin
from utils.tradeLogger import TradeLogger

apiKey = 'f8qMRApitW2Gkeymmq9kA9vSsp6W5S2U21OXkLk9'
accessToken = '7c0657e8ec714fe0bb7fbebbb1354b2b4f992857'


def storeCredentials():
    pass


def loadCredentials():
    pass


if __name__ == "__main__":
    try:
        TradeLogger.basicConfig()
        logging.info("This is an info message!")
        logging.debug("This is a debug message!")
        logging.trade("This is a trade message!")
    except Exception as e:
        logging.exception("Exception ocurred!")
