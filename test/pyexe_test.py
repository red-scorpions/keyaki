# !/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from helper import selenium_helper
import subprocess

subprocess.call("sh ../set_env.sh",shell=True)
driver = selenium_helper.access_yahoo()
driver.close()