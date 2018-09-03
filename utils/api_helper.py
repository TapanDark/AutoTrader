from upstox_api.api import *
import base64
import logging


class UpstoxHelper(object):

    def __init__(self, apiKey, accessToken=None):
        """
        :param apiKey: Upstox app API KEY
        :param apiSecret: Upstox app API SECRET
        :param redirectUrl: Redirect URL for app authentication
        :param accessCodeProvider: callable that accepts login url and returns access code upon authorization
        """
        self.apiKey = apiKey
        self.accessToken = accessToken
        self.session = None
        self.upstoxObj = None

    @staticmethod
    def getApiKey():
        with open(os.path.join(os.path.dirname(__file__), 'data', 'api_keys.txt'), 'r') as fp:
            data = json.loads(fp.read())
        return base64.b64decode(data['apiKey'])

    @staticmethod
    def getApiSecret():
        with open(os.path.join(os.path.dirname(__file__), 'data', 'api_keys.txt'), 'r') as fp:
            data = json.loads(fp.read())
        return base64.b64decode(data['apiSecret'])

    @staticmethod
    def getRedirectUrl():
        with open(os.path.join(os.path.dirname(__file__), 'data', 'api_keys.txt'), 'r') as fp:
            data = json.loads(fp.read())
        return base64.b64decode(data['redirect'])

    def authenticate(self, apiSecret, redirectUrl, accessCodeProvider):
        logging.debug("Trying to authenticate with:\napiKey:%s\napiSecret:%s\nredirect:%s" % (
            self.apiKey, apiSecret, redirectUrl))
        self.session = Session(self.apiKey)
        self.session.set_redirect_uri(redirectUrl)
        self.session.set_api_secret(apiSecret)
        accessCode = accessCodeProvider(self.session.get_login_url())
        assert accessCode, "Authentication failure! Did not receive access code."
        logging.debug("Recevied access code: %s" % accessCode)
        self.session.set_code(accessCode)
        self.accessToken = self.session.retrieve_access_token()
        logging.debug("Received accessToken: %s" % self.accessToken)

    def connect(self):
        if not self.accessToken:
            logging.error("Failed to create upstox object! Please authenticate first.")
            return False
        logging.debug("Creating upstox object with\napiKey: %s\naccessToken:%s" % (self.apiKey, self.accessToken))
        self.upstoxObj = Upstox(self.apiKey, self.accessToken)
        return True

    def getInstrument(self, symbol, exchange='NSE_EQ'):
        self.get_instrument_by_symbol(exchange, symbol)

    def __getattr__(self, item):
        if not self.upstoxObj:
            raise AttributeError
        return getattr(self.upstoxObj, item)


if __name__ == "__main__":
    from misc import automatedLogin
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--apiKey", default=None, type=str, help="Api key for upstox app")
    parser.add_argument("--apiSecret", default=None, type=str, help="Api secret for upstox app")
    parser.add_argument("--redirect", default=None, type=str, help="URL to authentication service.")
    parser.add_argument("--accessToken", default=None, type=str, help="Access token if authorized already.")
    arguments = parser.parse_args()
    apiKey = arguments.apiKey if arguments.apiKey else UpstoxHelper.getApiKey()
    apiSecret = arguments.apiSecret if arguments.apiSecret else UpstoxHelper.getApiSecret()
    redirect = arguments.redirect if arguments.redirect else UpstoxHelper.getRedirectUrl()
    uHelper = UpstoxHelper(apiKey, arguments.accessToken)
    if not arguments.accessToken:
        uHelper.authenticate(apiSecret, redirect, automatedLogin)
    uHelper.connect()
    import pdb

    pdb.set_trace()
    logging.info("Done")
