# !/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from helper import selenium_helper
import subprocess
from helper import os_helper

subprocess.call(os_helper.change_ps("sh ../set_env.sh"),shell=True)
driver = selenium_helper.access()
selenium_helper.login(driver)
