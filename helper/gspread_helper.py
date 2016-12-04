# !/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import os
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime


class gspread_helper(object):
    def __init__(self):
        scope = ['https://spreadsheets.google.com/feeds']
        doc_id = '1ORQg_26MJNrFisFxMfK_p8PcsrDuIXu6TNbd3bm1gTo'
        path = os.path.expanduser("./conf/API Project-476fa123229c.json")
        credentials = ServiceAccountCredentials.from_json_keyfile_name(path, scope)
        client = gspread.authorize(credentials)
        gfile = client.open_by_key(doc_id)
        year, month = self.get_next_year_and_month()
        self.new_sheet = gfile.worksheet(str(year) + "/" + str(month))
        self.school_sheet = gfile.worksheet("school_list")

    def get_next_year_and_month(self):
        today = datetime.datetime.now()
        one_month_later = today + datetime.timedelta(days=35)  # どの道抽選は1-4日しか使用しないし、予約を自動で行うのも10日だけなので、これでよい
        return one_month_later.year, one_month_later.month

    def get_weekend_and_holiday_list(self):
        date_list = self.new_sheet.row_values(1)
        date_list = [e for e in date_list if e != ""]
        return date_list

    def get_school_list(self):
        school_list = []
        gym_or_fight_list = []
        initial_list = []
        school_list = self.school_sheet.col_values(2)
        gym_or_fight_list = self.school_sheet.col_values(3)
        initial_list = self.school_sheet.col_values(4)
        school_list = self.trim_after_first_empty(school_list)
        gym_or_fight_list = self.trim_after_first_empty(gym_or_fight_list)
        initial_list = self.trim_after_first_empty(initial_list)
        return school_list, gym_or_fight_list, initial_list

    def trim_after_first_empty(self, list):
        first_empty_index = list.index('')
        return list[:first_empty_index]

    def write_cell(self,row,col,val):
        self.new_sheet.update_cell(row, col, val)