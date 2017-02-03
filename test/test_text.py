# !/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from helper import os_helper


driver = webdriver.Chrome(os_helper.change_ps('./chromedriver'))
driver.get('http://www.w3c.org')
element = driver.find_element_by_name('q')
element.send_keys('hi mom')

element_text = element.text
element_attribute_value = element.get_attribute('value')

print element
print 'element.text: {0}'.format(element_text)
print 'element.get_attribute(\'value\'): {0}'.format(element_attribute_value)
# driver.quit()
