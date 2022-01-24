import os
import time
from typing import Tuple
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
import datetime
from datetime import datetime,timedelta
import pause
from dotenv import load_dotenv
import re
from seleniumwire import webdriver  

def web_driver_init(): 
    options = Options()

    options.add_argument('--headless')
    options.add_argument("window-size=1440,1900")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('–incognito')


    driver = webdriver.Chrome(
        executable_path='/usr/local/bin/chromedriver', chrome_options=options)

    # driver.get("https://opensea.io/")
    # first_request = driver.requests[0]

    return driver

def goToOpensea(driver):
    driver.get("https://opensea.io/")
    # first_request = driver.requests[0]
    # print(first_request)

if __name__ == '__main__':
    driver = web_driver_init()
    goToOpensea(driver)

    for request in driver.requests:
        print(request)

