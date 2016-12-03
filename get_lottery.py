# !/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
import os

driver = webdriver.Chrome('./chromedriver')
driver.get('https://www.keyakinet.jp/w/')
apply_button = driver.find_element_by_id("BT0")
apply_button.click()



