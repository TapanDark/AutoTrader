from upstox_api.api import *
import logging

# DEFAULTS
API_KEY = "f8qMRApitW2Gkeymmq9kA9vSsp6W5S2U21OXkLk9"
API_SECRET = "zhkf8kk412"
REDIRECT_URL = 'https://upstox.com/'


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

    def __getattr__(self, item):
        return getattr(self.upstoxObj, item)


if __name__ == "__main__":
    from misc import automatedLogin
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--apiKey", default=API_KEY, type=str, help="Api key for upstox app")
    parser.add_argument("--apiSecret", default=API_SECRET, type=str, help="Api secret for upstox app")
    parser.add_argument("--redirect", default=REDIRECT_URL, type=str, help="URL to authentication service.")
    parser.add_argument("--accessToken", default=None, type=str, help="Access token if authorized already.")
    arguments = parser.parse_args()
    import pdb

    pdb.set_trace()
    uHelper = UpstoxHelper(arguments.apiKey, arguments.accessToken)
    if not arguments.accessToken:
        uHelper.authenticate(arguments.apiSecret, arguments.redirect, automatedLogin)
    uHelper.connect()
