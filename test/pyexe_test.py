# !/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
import platform
if platform.system() == "Windows":
    os.system("..\set_env.bat")
else:
    subprocess.call(("sh ../set_env.sh"),shell=True)
import sys
if platform.system() == "Windows":
    sys.path.append("..")
print sys.path


from helper import selenium_helper
from helper import os_helper

driver = selenium_helper.access_yahoo()
driver.close()

