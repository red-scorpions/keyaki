# !/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from helper import selenium_helper
import subprocess

subprocess.call("sh ../set_env.sh",shell=True)
driver = selenium_helper.access()
selenium_helper.login(driver)
selenium_helper.change_school_and_get_count(driver)
driver.close()