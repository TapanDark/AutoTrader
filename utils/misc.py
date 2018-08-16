import os
import itertools
import logging


def generateIncrementingPath(path):
    def incrementPath(path):
        if os.path.isfile(path):
            basePath, extension = os.path.splitext(path)
            extension = ".%s" % extension
        else:
            basePath = path
            extension = ""
        yield basePath + extension
        for n in itertools.count(start=1, step=1):
            yield '%s_%d%s' % (basePath, n, extension)

    for newPath in incrementPath(path):
        if not os.path.exists(newPath):
            logging.debug("Found new path name:%s" % path)
            return newPath
        logging.debug("Path already exists:%s" % newPath)


def mkdir(dirpath):
    logging.debug("Creating directory: %s" % dirpath)
    try:
        os.makedirs(dirpath)
    except Exception as e:
        logging.warning("Unable to create directory: %s" % dirpath)
