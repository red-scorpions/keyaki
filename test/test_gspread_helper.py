# !/usr/bin/env python
# -*- coding: utf-8 -*-

from helper import gspread_helper

import subprocess
from helper import os_helper

subprocess.call(os_helper.change_ps("sh ../set_env.sh"),shell=True)
GH = gspread_helper.GspreadHelper()
GH.write_cell(1,1,0)
GH.write_cell(1,2,1)
GH.write_cell(2,1,2)
GH.write_cell(2,2,3)
# print GH.get_school_list()
