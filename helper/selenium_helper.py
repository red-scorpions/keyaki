# !/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import os
import time
from helper import gspread_helper
import datetime
import platform

def access():
    if platform.system() == "Windows":
        driver = webdriver.Chrome('../driver/windows/chromedriver.exe')
    else:
        driver = webdriver.Chrome('../driver/mac/chromedriver')
    driver.get('https://www.keyakinet.jp/w/')
    # デバッグ時はpage_source使うとよくわかるよ
    # f = open("./page_source_top.txt", "wa")
    # f.write(driver.page_source.encode('utf_8'))
    # f.close()
    iframe = driver.find_element_by_name("iframe")
    time.sleep(1)
    driver.switch_to.frame(iframe)
    driver = _click(driver, 'BB0')
    return driver

def login(driver):
    row = 0
    for line in open("../conf/id_and_pass.txt", 'r'):
        if row == 1:
            user_info = line.split(",")
            break
        row += 1
    time.sleep(1)
    ActionChains(driver).send_keys(user_info[0]).send_keys(user_info[1]).send_keys(user_info[2]).perform()


def change_school_and_get_count(driver):
    GH = gspread_helper.gspread_helper()
    school_list, gym_or_fight_list, initial_list = GH.get_school_list()
    year, month = GH.get_next_year_and_month()
    weekend_and_holiday_list = GH.get_weekend_and_holiday_list()
    len_school_list = len(school_list)
    len_date_list = len(weekend_and_holiday_list)
    for i in range(len_school_list):
        _choose_initial(driver, initial_list[i])
        _choose_school(driver, school_list[i])
        _to_top(driver)
        _to_calendar(driver, school_list[i], gym_or_fight_list[i])
        count_list = get_count_list(driver, year, month, weekend_and_holiday_list)
        _to_top(driver)
        for j in range(len_date_list):
            GH.write_cell(i + 3, j + 4, count_list[j])


def _choose_initial(driver, initial):
    driver = _click(driver, 'BB4')
    driver = _click(driver, 'BB5')
    _choose_and_click(driver, "div.SELINI", initial)
    return driver


def _choose_school(driver, school):
    find_flag = False
    while not find_flag:
        driver, find_flag = _choose_school_one_page(driver, school)
    driver = _click(driver, 'FB2')


def _choose_school_one_page(driver, school):
    driver, find_flag = _choose_and_click(driver, "div.SELTXT", school)
    if not find_flag:
        driver = _click(driver, 'VB2')
    return driver, find_flag


def _to_top(driver):
    driver = _click(driver, 'FOOT2BTN')


def _to_calendar(driver, school, gym_or_fight):
    driver = _click(driver, 'BB3')
    driver = _click(driver, 'FOOT5BTN')
    driver, find_flag = _choose_and_click(driver, "div.SELTXT", school)
    driver, find_flag = _choose_and_click(driver, "div.SELTXT", u"屋内スポーツ")
    driver, find_flag = _choose_and_click(driver, "div.SELTXT", u"バレーボール")
    driver, find_flag = _choose_and_click(driver, "div.SELTXT", gym_or_fight)


def get_count_list(driver, year, month, weekend_and_holiday_list):
    count_list = []
    active_date_count = 100
    while active_date_count > 0:
        active_date_count = 0
        active_flag_list, row_div_list = _get_active_flag_list(driver)
        print active_flag_list
        active_date_count = len([e for e in active_flag_list if e])
        date_div_list = _fetch_list(driver, "div.DAYTX")
        date_info_list = [d.text for d in date_div_list]
        date_list = [_get_date_from_date_info(date_info) for date_info in date_info_list]
        print date_list
        for i in range(7):
            if active_flag_list[i] and str(year) + "/" + str(month) + "/" + str(
                    date_list[i]) in weekend_and_holiday_list:
                print date_list[i]
                table = row_div_list[i].find_elements_by_css_selector("table")[-1]
                tbody = table.find_element_by_css_selector("tbody")
                tr = tbody.find_elements_by_css_selector("tr")[-1]
                td = tr.find_elements_by_css_selector("td")[-1]
                if len(td.find_elements_by_css_selector("img")) > 0:
                    count_list.append('')
                else:
                    count_with_ken = td.text
                    count_list.append(remove_ken(count_with_ken))
        if active_date_count > 0:
            driver = _click(driver, 'NEXTWEEKBTN')
    return count_list


def remove_ken(text):
    ken_index = text.index(u"件")
    return int(text[:ken_index])


def _get_active_flag_list(driver):
    bool_list = []
    div_list = []
    for i in range(1, 8):
        div = driver.find_element_by_css_selector("div#DAY{}".format(i))
        div_list.append(div)
        bool_list.append(len(div.find_elements_by_css_selector("input.DAYBTN")) > 0)
    return bool_list, div_list


def _fetch_list(driver, selector):
    list_ = driver.find_elements_by_css_selector(selector)
    return list_


def _get_date_from_date_info(date_info):
    month_index = date_info.index(u"月")
    date_index = date_info.index(u"日")
    date = int(date_info[month_index + 1:date_index])
    return date


def _get_count_from_table(ele):
    return count_


def _judge_weekend_and_hodiday(driver, i):
    is_weekend_and_holiday = False
    return is_weekend_and_holiday


def _click(driver, id):
    button = driver.find_element_by_xpath("//input[@id='{}']".format(id))
    button.click()
    return driver


def _choose_and_click(driver, selector, ele):
    find_flag = False
    list_ = driver.find_elements_by_css_selector(selector)
    for ele_list in list_:
        if ele_list.text == ele:
            # print ele
            ele_list.click()
            find_flag = True
            return driver, find_flag
    return driver, find_flag