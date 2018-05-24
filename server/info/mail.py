from __future__ import print_function
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pprint import *
import time

# Things you need to modify >>>>
options = Options()
options.add_experimental_option("prefs", {
    "download.default_directory": r"/home/deepak_saini/Desktop/",
    "download.prompt_for_download": False,
})


def send_mail(mail_add, title, message):
    driver = webdriver.Firefox(
        executable_path="/home/db1/Documents/Softi_project/geckodriver")
    url = 'https://www.google.com/accounts/Login?hl=ja&continue=http://www.google.co.jp/'
    driver.get(url)
    # >>>>gmail username and password
    driver.find_element_by_id("identifierId").send_keys(
        "sainideepak119@gmail.com")
    driver.find_element_by_id("identifierNext").click()
    time.sleep(3)
    # >>>>
    driver.find_element_by_xpath(
        "//input[@type='password']").send_keys("Sai500081")
    driver.find_element_by_id("passwordNext").click()
    time.sleep(3)
    driver.get("https://mail.google.com/")
    time.sleep(5)
    driver.find_element_by_xpath(
        "//div[@class='T-I J-J5-Ji T-I-KE L3']").click()
    time.sleep(3)
    driver.find_element_by_xpath("//textarea[@name='to']").send_keys(mail_add)
    driver.find_element_by_xpath("//input[@class='aoT']").send_keys(title)
    driver.find_element_by_xpath(
        "//div[@class='Am Al editable LW-avf']").send_keys(message)
    driver.find_element_by_xpath("//div[@id=':o6']").click()


if __name__ == '__main__':
    send_mail("sainideepak119@gmail.com", "Testing", "Hello There!!")
