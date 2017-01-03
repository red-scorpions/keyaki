# !/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import os
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime


class GspreadHelper(object):
    def __init__(self):
        scope = ['https://spreadsheets.google.com/feeds']
        for line in open("../conf/key_id.txt", 'r'):
            doc_id = line
        path = "../conf/API Project-476fa123229c.json"
        credentials = ServiceAccountCredentials.from_json_keyfile_name(path, scope)
        client = gspread.authorize(credentials)
        gfile = client.open_by_key(doc_id)
        year, month = self.get_next_year_and_month()
        current_ver = 0
        # todo current_verを正しい値にする
        worksheets = gfile.worksheets()
        current_ver = 0
        for worksheet in worksheets:
            if str(year) + "/" + str(month) + "_asa_" in worksheet.title:
                current_ver += 1
        # シート名取得
        if current_ver == 0:
            print("シート作成ができていないと思います。まずシートを作りましょう。")
            assert(False)
        self.new_sheet_asa = gfile.worksheet(str(year) + "/" + str(month) + "_asa_" + str(current_ver))
        self.new_sheet_yoru = gfile.worksheet(str(year) + "/" + str(month) + "_yoru_" + str(current_ver))
        self.school_sheet = gfile.worksheet("school_list")

    def get_next_year_and_month(self):
        today = datetime.datetime.now()
        one_month_later = today + datetime.timedelta(days=35)  # どの道抽選は1-4日しか使用しないし、予約を自動で行うのも10日だけなので、これでよい
        return one_month_later.year, one_month_later.month

    def get_weekend_and_holiday_list(self):
        date_list = self.new_sheet_asa.row_values(1)
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
        # まず最初の空白を除く
        list = list[1:]
        # その上で、最初の空白の前までを残す
        first_empty_index = list.index('')
        return list[:first_empty_index]

    def write_cell(self, row, col, val, asa_flag):
        if asa_flag:
            self.new_sheet_asa.update_cell(row, col, val)
        else:
            self.new_sheet_yoru.update_cell(row, col, val)
