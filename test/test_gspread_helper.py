# !/usr/bin/env python
# -*- coding: utf-8 -*-

from helper import gspread_helper



GH = gspread_helper.gspread_helper()
print GH.get_school_list()
