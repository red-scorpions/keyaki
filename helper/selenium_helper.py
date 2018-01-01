# !/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import os
import time
from helper import gspread_helper
import datetime
import platform
from helper import os_helper


def access():
    if platform.system() == "Windows":
        driver = webdriver.Chrome(os_helper.change_ps('../driver/windows/chromedriver.exe'))
    else:
        driver = webdriver.Chrome(os_helper.change_ps('../driver/mac/chromedriver'))
    driver.get('https://www.keyakinet.jp/w/')
    # driver.implicitly_wait(30)
    time.sleep(10)
    iframe = driver.find_element_by_name("iframe")
    time.sleep(1)
    driver.switch_to.frame(iframe)
    driver = _click(driver, 'BB0')
    return driver


def access_yahoo():
    if platform.system() == "Windows":
        driver = webdriver.Chrome(os_helper.change_ps('../driver/windows/chromedriver.exe'))
    else:
        driver = webdriver.Chrome(os_helper.change_ps('../driver/mac/chromedriver'))
    driver.get('http://www.yahoo.co.jp/')
    # デバッグ時はpage_source使うとよくわかるよ
    # f = open("./page_source_top.txt", "wa")
    # f.write(driver.page_source.encode('utf_8'))
    # f.close()
    return driver


def login(driver):
    row = 0
    for line in open(os_helper.change_ps("../conf/id_and_pass.txt"), 'r'):
        if row == 1:
            user_info = line.split(",")
            break
        row += 1
    time.sleep(1)
    ActionChains(driver).send_keys(user_info[0]).send_keys(user_info[1]).send_keys(user_info[2]).perform()


def change_school_and_get_count(driver):
    GH = gspread_helper.GspreadHelper()
    school_list, gym_or_fight_list, initial_list = GH.get_school_list()
    year, month = GH.get_next_year_and_month()
    weekend_and_holiday_list = GH.get_weekend_and_holiday_list()
    len_school_list = len(school_list)
    # print("finish counting_len_school_list:{}".format(len_school_list))
    len_date_list = len(weekend_and_holiday_list)
    # print("finish counting_len_date_list:{}".format(len_date_list))
    for i in range(len_school_list):
        if platform.system() == "Windows":
            print("{}th school start:{}".format(i, school_list[i].encode('shift-jis')))
        else:
            print("{}th school start:{}".format(i, school_list[i].encode('utf-8')))
        _choose_initial(driver, initial_list[i])
        print("_choose_initial done")
        _choose_school(driver, school_list[i])
        print("_choose_school done")
        _to_top(driver)
        print("_to_top done")
        _to_calendar(driver, school_list[i], gym_or_fight_list[i])
        print("_to_calendar done")
        count_list_asa, count_list_hirua, count_list_hirub, count_list_yoru = _get_count_list(driver, year, month,
                                                                                              weekend_and_holiday_list)
        print("_get_count_list done")
        _to_top(driver)
        print("_to_top done")
        for j in range(len_date_list):
            GH.write_cell(i + 3, j + 4, count_list_asa[j], sheet_type="asa")
            GH.write_cell(i + 3, j + 4, count_list_hirua[j], sheet_type="hirua")
            GH.write_cell(i + 3, j + 4, count_list_hirub[j], sheet_type="hirub")
            GH.write_cell(i + 3, j + 4, count_list_yoru[j], sheet_type="yoru")
        print("{}th school end".format(i))
    print("全体育館の情報を取得完了しました。")


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


def _get_count_list(driver, year, month, weekend_and_holiday_list):
    count_list_asa = []
    count_list_hirua = []
    count_list_hirub = []
    count_list_yoru = []
    active_date_count = 100
    while active_date_count > 0:
        active_date_count = 0
        active_flag_list, row_div_list = _get_active_flag_list(driver)
        # print(active_flag_list)
        # print(active_flag_list)
        active_date_count = len([e for e in active_flag_list if e])
        date_div_list = _fetch_list(driver, "div.DAYTX")
        date_info_list = [d.text for d in date_div_list]
        date_list = [_get_date_from_date_info(date_info) for date_info in date_info_list]
        print(date_list)
        for i in range(7):
            if active_flag_list[i] and str(year) + "/" + str(month) + "/" + str(
                    date_list[i]) in weekend_and_holiday_list:
                # print(date_list[i])
                table = row_div_list[i].find_elements_by_css_selector("table")[-1]
                tbody = table.find_element_by_css_selector("tbody")
                tr = tbody.find_elements_by_css_selector("tr")[-1]
                # 朝
                td_asa = tr.find_elements_by_css_selector("td")[0]
                if len(td_asa.find_elements_by_css_selector("img")) > 0:
                    count_list_asa.append('')
                else:
                    count_with_ken = td_asa.text
                    count_list_asa.append(_remove_ken(count_with_ken))
                # 昼A
                td_hirua = tr.find_elements_by_css_selector("td")[1]
                if len(td_hirua.find_elements_by_css_selector("img")) > 0:
                    count_list_hirua.append('')
                else:
                    count_with_ken = td_hirua.text
                    count_list_hirua.append(_remove_ken(count_with_ken))
                # 昼B
                td_hirub = tr.find_elements_by_css_selector("td")[2]
                if len(td_hirub.find_elements_by_css_selector("img")) > 0:
                    count_list_hirub.append('')
                else:
                    count_with_ken = td_hirub.text
                    count_list_hirub.append(_remove_ken(count_with_ken))
                # 夜
                td_yoru = tr.find_elements_by_css_selector("td")[-1]
                if len(td_yoru.find_elements_by_css_selector("img")) > 0:
                    count_list_yoru.append('')
                else:
                    count_with_ken = td_yoru.text
                    count_list_yoru.append(_remove_ken(count_with_ken))
        if active_date_count > 0:
            driver = _click(driver, 'NEXTWEEKBTN')
    return count_list_asa, count_list_hirua, count_list_hirub, count_list_yoru


def _remove_ken(text):
    ken_index = text.index(u"件")
    return int(text[:ken_index])


def _get_active_flag_list(driver):
    bool_list = []
    div_list = []
    for i in range(1, 8):
        div = driver.find_element_by_css_selector("div#DAY{}".format(i))
        div_list.append(div)
        try:
            len_daybtn = len(div.find_elements_by_css_selector("input.DAYBTN"))
            bool_list.append(len_daybtn > 0)
        except:
            bool_list.append(False)
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
            # print(ele)
            ele_list.click()
            find_flag = True
            return driver, find_flag
    return driver, find_flag
