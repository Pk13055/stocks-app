from selenium import webdriver
from upstox_api.api import Session
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from urllib.parse import urlparse, parse_qs
import os

cwd = os.getcwd()

def autologin():
    s = Session('AAJ0Rx0qDu5TExtIOhEIH1od78siET7t6SuMiGsO')
    s.set_redirect_uri ('http://127.0.0.1')
    s.set_api_secret ('7qofcpddrl')
    #driver = webdriver.Chrome('/home/ubuntu/stocks-app/chromedriver')
    service = webdriver.chrome.service.Service('./chromedriver')
    service.start()
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options = options.to_capabilities()
    driver = webdriver.Remote(service.service_url, options)
    driver.get(s.get_login_url())
    driver.implicitly_wait(10)
    username = driver.find_element_by_xpath('//*[@id="name"]')
    password = driver.find_element_by_xpath('//*[@id="password"]')
    dob = driver.find_element_by_xpath('//*[@id="password2fa"]')
    username.send_keys("142629")
    password.send_keys("Shermin200!")
    dob.send_keys("1984")
    driver.find_element_by_xpath('/html/body/form/fieldset/div[3]/div/button').click()
    driver.find_element_by_xpath('//*[@id="allow"]').click()
    x=driver.current_url
    y=x.split('=')
    generate_session = y[1]
    text_file = open(os.path.join(cwd,"generate_session.txt"), "w")
    text_file.write(generate_session)
    text_file.close()
    gen=open(os.path.join(cwd,"generate_session.txt"),'r').read()
    s.set_code (gen)
    access_token = s.retrieve_access_token()
    text_file = open(os.path.join(cwd,"access_token.txt"), "w")
    text_file.write(access_token)
    text_file.close()
    driver.quit()
autologin()







