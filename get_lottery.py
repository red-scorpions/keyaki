# !/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
import os
import time
driver = webdriver.Chrome('./chromedriver')
driver.get('https://www.keyakinet.jp/w/')
print type(driver)
print driver
ele_iframe = driver.find_element_by_name("iframe")
time.sleep(5)
print type(ele_iframe)
print ele_iframe
# ele_contid = ele_iframe.find_element_by_id("CONTID")
# print ele_contid
# apply_button = ele_iframe.find_element_by_xpath("//input[@id='BB0']")
apply_button = driver.find_element_by_xpath("//input[@id='BB0']")
# apply_button = ele_iframe.find_element_by_id("BB0")
apply_button.click()



