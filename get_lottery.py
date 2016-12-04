# !/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from helper import selenium_helper
import commands

commands.getoutput("sh set_env.sh")
driver = selenium_helper.access()
selenium_helper.login(driver)
selenium_helper.change_school_and_get_count(driver)