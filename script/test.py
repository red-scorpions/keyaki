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

school_list = ["ア小学校","イ小学校","ウ小学校"]
loaded_list = ["済","未","済"]
filtered_school_list = selenium_helper.filter_school_list(school_list,loaded_list)
print(filtered_school_list)
