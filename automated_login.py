import json
import os
import base64

from selenium import webdriver
from urlparse import urlparse

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
