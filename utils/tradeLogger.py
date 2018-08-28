import logging
import datetime
import sys
import os

from utils.misc import generateIncrementingPath, mkdir

TRADE_LEVEL = 60


def trade(self, message, *args, **kws):
    # Yes, logger takes its '*args' as 'args'.
    if self.isEnabledFor(TRADE_LEVEL):
        self._log(TRADE_LEVEL, message, args, **kws)


def module_trade(msg, *args, **kwargs):
    if len(logging.root.handlers) == 0:
        logging.basicConfig()
    logging.root.trade(msg, *args, **kwargs)


class TradeLogger(object):
    _debugFormat = '[%(asctime)s] [%(levelname)s] [Function %(funcName)s] Line %(lineno)s: File %(filename)s: %(message)s'
    _tradeFormat = '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
    _format = '[%(asctime)s] [%(levelname)s] %(message)s'
    _dateFormat = '%m/%d/%Y %H:%M:%S'
    logger = logging.getLogger()  # get root logger

    @classmethod
    def setStreamLogger(cls, streamIO, logLevel=logging.DEBUG if sys.flags.debug else logging.INFO):
        if not getattr(streamIO, 'write', None):
            raise Exception("Invalid stream handle provided for logging.")
        streamHandle = logging.StreamHandler(streamIO)
        streamHandle.setLevel(logLevel)
        if logLevel == logging.DEBUG:
            streamHandle.setFormatter(logging.Formatter(cls._debugFormat, datefmt=cls._dateFormat))
        else:
            streamHandle.setFormatter(logging.Formatter(cls._format, datefmt=cls._dateFormat))
        cls.logger.addHandler(streamHandle)

    @classmethod
    def setFileLoggers(cls, logDir, simulation, logTime=None):
        if not logTime:
            logTime = datetime.datetime.now()
        logDir = generateIncrementingPath(
            os.path.join(logDir, str(logTime.year), logTime.strftime("%b"), str(logTime.day),
                         "%s" % ('simulation' if simulation else 'real'), 'iter'))
        if not os.path.isabs(logDir):
            logDir = os.path.join(os.getcwd(), logDir)
        mkdir(logDir)
        stdoutHandler = logging.FileHandler(os.path.join(logDir, 'stdout.log'))
        stdoutFormatter = logging.Formatter(cls._format, datefmt=cls._dateFormat)
        stdoutHandler.setFormatter(stdoutFormatter)
        stdoutHandler.setLevel(logging.INFO)
        cls.logger.addHandler(stdoutHandler)

        debugHandler = logging.FileHandler(os.path.join(logDir, 'stdout.debug.log'))
        debugFormatter = logging.Formatter(cls._debugFormat, datefmt=cls._dateFormat)
        debugHandler.setFormatter(debugFormatter)
        debugHandler.setLevel(logging.DEBUG)
        cls.logger.addHandler(debugHandler)

        tradeHandler = logging.FileHandler(os.path.join(logDir, 'trade.log'))
        tradeFormatter = logging.Formatter(cls._tradeFormat, datefmt=cls._dateFormat)
        tradeHandler.setFormatter(tradeFormatter)
        tradeHandler.setLevel(TRADE_LEVEL)  # Custom "TRADE" level
        cls.logger.addHandler(tradeHandler)

    @classmethod
    def basicConfig(cls, logDir='TraderLogs', logLevel=logging.DEBUG if sys.flags.debug else logging.INFO,
                    simulation=True, logTime=None):
        logging.addLevelName(TRADE_LEVEL, "TRADE")
        logging.Logger.trade = trade
        logging.trade = module_trade
        cls.logger.setLevel(logging.DEBUG)
        if len(cls.logger.handlers) == 0:
            cls.setStreamLogger(sys.stdout, logLevel=logLevel)
            cls.setFileLoggers(logDir, simulation, logTime=logTime)
