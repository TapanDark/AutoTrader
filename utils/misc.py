import base64
import itertools
import json
import logging
import os
from urlparse import urlparse

from selenium import webdriver


def generateIncrementingPath(path):
    def incrementPath(path):
        if os.path.isfile(path):
            basePath, extension = os.path.splitext(path)
            extension = ".%s" % extension
        else:
            basePath = path
            extension = ""
        yield basePath + extension
        for n in itertools.count(start=2, step=1):
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


def automatedLogin(url):
    browser = webdriver.Chrome(executable_path=r"chromedriver.exe")
    browser.get(url)
    with open(os.path.join(os.path.dirname(__file__), 'data', 'passdata.txt'), 'r') as fp:
        data = json.loads(fp.read())
    userId = browser.find_element_by_name('username')
    userId.send_keys(base64.b64decode(data['username']))
    password = browser.find_element_by_name('password')
    password.send_keys(base64.b64decode(data['password']))
    password2fa = browser.find_element_by_name('password2fa')
    password2fa.send_keys(base64.b64decode(data['password2fa']))
    browser.find_element_by_class_name("sign-in-button").click()
    browser.find_element_by_id("allow").click()
    urlObj = urlparse(browser.current_url)
    assert urlObj.query.split('=')[0] == 'code', "Could not authenticate successfully"
    accessCode = urlObj.query.split('=')[1]
    assert accessCode, "Could not get access code from redirect url!"
    browser.close()
    return accessCode
