# !/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
import platform
import sys
if platform.system() == "Windows":
    os.system("..\setup\set_env.bat")
else:
    subprocess.call(("sh ../setup/set_env.sh"),shell=True)
sys.path.append("..")

from helper import selenium_helper

driver = selenium_helper.access()
selenium_helper.login(driver)
selenium_helper.change_school_and_get_count(driver)
driver.close()