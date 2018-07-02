# !/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
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
    driver.get("https://setagaya.keyakinet.net/Web/Home/WgR_ModeSelect")
    driver.find_element_by_link_text(u"ログイン").click()
    # 下記の書き方でもよい
    # xpath = "//div[@id='head']/div/p/a"
    # driver.execute_script("var xPathRes = document.evaluate('//div[@id=\"head\"]/div/p/a',document,null,9,null).singleNodeValue.click();")
    driver.implicitly_wait(30)
    return driver


def login(driver):
    row = 0
    for line in open(os_helper.change_ps("../conf/id_and_pass.txt"), 'r'):
        if row == 1:
            user_info = line.split(",")
            break
        row += 1
    time.sleep(1)
    driver.find_element_by_id("userID").send_keys(user_info[0])
    driver.find_element_by_id("passWord").send_keys(user_info[1])
    time.sleep(2)
    ActionChains(driver).move_by_offset(10, 10).click().perform()  # ポップアップを消す


def get_count_main(driver):
    GH = gspread_helper.GspreadHelper()
    school_list, gym_or_fight_list, initial_list = GH.get_school_list()
    weekend_and_holiday_list = GH.get_weekend_and_holiday_list()
    # print("finish counting_len_school_list:{}".format(len_school_list))
    len_date_list = len(weekend_and_holiday_list)
    # print("finish counting_len_date_list:{}".format(len_date_list))
    _click_search_school(driver, school_list,weekend_and_holiday_list, len_date_list,GH)
    print("全体育館の情報を取得完了しました。")


def _click_search_school(driver, school_list,weekend_and_holiday_list, len_date_list,GH):
    driver.find_element_by_link_text(u"使用目的から探す").click()
    driver.find_element_by_xpath("//div[@id='tabs']/div[2]/div/ul/li[3]/label").click()
    time.sleep(1)
    driver.find_element_by_xpath("//div[@id='mokutekiForm']/ul/li[4]/label").click()
    driver.find_element_by_id("btnSearchViaPurpose").click()
    time.sleep(2)
    read_more_link_text = u"さらに読み込む"
    is_read_more = True
    driver.implicitly_wait(3)
    while is_read_more:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.8)
        driver.find_element_by_link_text(read_more_link_text).click()
        is_read_more = is_element_present(driver, By.LINK_TEXT, read_more_link_text)
        time.sleep(1.8)
    is_school = True
    k = 1
    i = 0
    school_xpath_base = "//tbody[@id='shisetsutbl']/tr{0}/td[2]/label"
    cell_height = int(driver.find_element_by_xpath("//tbody[@id='shisetsutbl']/tr/td[2]").size["height"])
    while is_school:
        driver.execute_script("window.scrollTo(0, {});".format((k - 1) * cell_height))
        time.sleep(1)
        school_xpath = school_xpath_base.format("" if k == 1 else "[{0}]".format(k))
        school = driver.find_element_by_xpath(school_xpath).text
        if school in school_list:
            driver.find_element_by_xpath(school_xpath).click()
            driver.find_element_by_id("btnNext").click()
            if i == 0:
                _change_start_date_and_period(driver)
            get_count_main_each_school(i, school_list, weekend_and_holiday_list, len_date_list,GH, driver)
            driver.find_element_by_xpath(school_xpath).click()
            i += 1
        k += 1
        school_xpath = school_xpath_base.format("" if k == 1 else "[{0}]".format(k))
        is_school = is_element_present(driver, By.XPATH, school_xpath)


def _change_start_date_and_period(driver):
    driver.find_element_by_id("dpStartDate").click()
    driver.find_element_by_xpath("//div[@id='ui-datepicker-div']/div/a[2]/span").click()
    driver.find_element_by_link_text("1").click()
    driver.find_element_by_id("lblPeriod1month").click()
    driver.find_element_by_id("btnHyoji").click()


def get_count_main_each_school(i, school_list, weekend_and_holiday_list, len_date_list,GH, driver):
    print("{}th school start:{}".format(i, school_list[i]))
    # print("weekend_and_holiday_list:{}".format(weekend_and_holiday_list))
    count_list_asa, count_list_hirua, count_list_hirub, count_list_yoru = _chooose_school_and_get_count_list(driver,
                                                                                                             school_list[
                                                                                                                 i],
                                                                                                             weekend_and_holiday_list)
    # print("len")
    # print(len(count_list_asa))
    # print(len(count_list_hirua))
    # print(len(count_list_hirua))
    # print(len(count_list_yoru))
    for j in range(len_date_list):
        # print(j)
        GH.write_cell(i + 3, j + 4, count_list_asa[j], sheet_type="asa")
        GH.write_cell(i + 3, j + 4, count_list_hirua[j], sheet_type="hirua")
        GH.write_cell(i + 3, j + 4, count_list_hirub[j], sheet_type="hirub")
        GH.write_cell(i + 3, j + 4, count_list_yoru[j], sheet_type="yoru")
    print("{}th school end".format(i))


def _chooose_school_and_get_count_list(driver, school, weekend_and_holiday_list):
    displayed_school_xpath_base = "//div[@id='body']/div[2]/div[3]/div[{0}]/h3/a"
    j = 1
    displayed_school_xpath = displayed_school_xpath_base.format(j)
    div = "//div[@id='body']/div[2]/div[3]/div[1]"
    div_height = int(driver.find_element_by_xpath(div).size["height"])
    for weekend_and_holiday in weekend_and_holiday_list:
        date = datetime.datetime.strptime(weekend_and_holiday, "%Y/%m/%d").day
        # print("date:{}".format(date))
        xpath = "//div[@id=\"body\"]/div[2]/div[3]/div[{0}]/div[2]/table/tbody/tr/td[{1}]/label".format(j,
                                                                                                        int(
                                                                                                            date) + 1)
        driver.execute_script(
            "document.evaluate('{0}',document,null,9,null).singleNodeValue.click()".format(xpath))
    driver.find_element_by_link_text(u"次へ進む").click()
    count_list_asa, count_list_hirua, count_list_hirub, count_list_yoru = _get_count_list(driver,
                                                                                          weekend_and_holiday_list)
    driver.find_element_by_link_text(u"前に戻る").click()
    driver.find_element_by_link_text(u"前に戻る").click()
    return count_list_asa, count_list_hirua, count_list_hirub, count_list_yoru


def _get_count_list(driver, weekend_and_holiday_list):
    count_list_asa = []
    count_list_hirua = []
    count_list_hirub = []
    count_list_yoru = []
    # //div[@id='body']/div[2]/div[2]/div/div[2]/table/tbody/tr/td[2]/label
    # //div[@id='body']/div[2]/div[2]/div/div[2]/table/tbody/tr/td[3]/label
    # //div[@id='body']/div[2]/div[2]/div/div[3]/table/tbody/tr/td[2]/label
    # //div[@id='body']/div[2]/div[2]/div/div[3]/table/tbody/tr/td[3]/label
    date_xpath_base = "//div[@id='body']/div[2]/div[2]/div/div[{0}]/table/tbody/tr/td[{1}]/label"
    div_base = "//div[@id='body']/div[2]/div[2]/div/div[{0}]"
    for k in range(len(weekend_and_holiday_list)):
        # 朝
        date_xpath = date_xpath_base.format(k + 2, 2)
        count_with_chusen = driver.find_element_by_xpath(date_xpath).text
        # print("朝: " + count_with_chusen)
        if "抽選" in count_with_chusen:
            count_list_asa.append(_remove_chusen(count_with_chusen))
        else:
            count_list_asa.append('')
        # 昼A
        date_xpath = date_xpath_base.format(k + 2, 3)
        count_with_chusen = driver.find_element_by_xpath(date_xpath).text
        # print("昼A: " + count_with_chusen)
        if "抽選" in count_with_chusen:
            count_list_hirua.append(_remove_chusen(count_with_chusen))
        else:
            count_list_hirua.append('')
        # 昼B
        date_xpath = date_xpath_base.format(k + 2, 4)
        count_with_chusen = driver.find_element_by_xpath(date_xpath).text
        # print("昼B: " + count_with_chusen)
        if "抽選" in count_with_chusen:
            count_list_hirub.append(_remove_chusen(count_with_chusen))
        else:
            count_list_hirub.append('')
        # 夜
        date_xpath = date_xpath_base.format(k + 2, 5)
        count_with_chusen = driver.find_element_by_xpath(date_xpath).text
        # print("夜: " + count_with_chusen)
        if "抽選" in count_with_chusen:
            count_list_yoru.append(_remove_chusen(count_with_chusen))
        else:
            count_list_yoru.append('')
        div_height = int(driver.find_element_by_xpath(div_base.format(k + 2)).size["height"])
        driver.execute_script("window.scrollTo(0, {});".format((k + 1) * div_height))
    return count_list_asa, count_list_hirua, count_list_hirub, count_list_yoru


def _remove_chusen(text):
    ken_start_index = text.index(u"（")
    ken_end_index = text.index(u"）")
    return int(text[ken_start_index + 1:ken_end_index])


def is_element_present(driver, how, what):
    try:
        driver.find_element(by=how, value=what)
    except NoSuchElementException as e:
        return False
    return True
