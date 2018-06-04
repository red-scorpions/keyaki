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
    year, month = GH.get_next_year_and_month()
    weekend_and_holiday_list = GH.get_weekend_and_holiday_list()
    len_school_list = len(school_list)
    # print("finish counting_len_school_list:{}".format(len_school_list))
    len_date_list = len(weekend_and_holiday_list)
    # print("finish counting_len_date_list:{}".format(len_date_list))
    _click_search_school(driver, school_list)
    _change_start_date_and_period(driver)
    for i in range(len_school_list):
        if platform.system() == "Windows":
            print("{}th school start:{}".format(i, school_list[i]))
        else:
            print("{}th school start:{}".format(i, school_list[i].encode('utf-8')))
        print("weekend_and_holiday_list:{}".format(weekend_and_holiday_list))
        count_list_asa, count_list_hirua, count_list_hirub, count_list_yoru = _chooose_school_and_get_count_list(driver,
                                                                                                                 school_list[
                                                                                                                     i],
                                                                                                                 weekend_and_holiday_list)
        print("_get_count_list done")
        print("_to_top done")
        for j in range(len_date_list):
            GH.write_cell(i + 3, j + 4, count_list_asa[j], sheet_type="asa")
            GH.write_cell(i + 3, j + 4, count_list_hirua[j], sheet_type="hirua")
            GH.write_cell(i + 3, j + 4, count_list_hirub[j], sheet_type="hirub")
            GH.write_cell(i + 3, j + 4, count_list_yoru[j], sheet_type="yoru")
        print("{}th school end".format(i))
    print("全体育館の情報を取得完了しました。")


def _click_search_school(driver, school_list):
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
        time.sleep(1.5)
        driver.find_element_by_link_text(read_more_link_text).click()
        is_read_more = is_element_present(driver, By.LINK_TEXT, read_more_link_text)
        time.sleep(1.5)
    is_school = True
    i = 1
    school_xpath_base = "//tbody[@id='shisetsutbl']/tr{0}/td[2]/label"
    cell_height = int(driver.find_element_by_xpath("//tbody[@id='shisetsutbl']/tr/td[2]").size["height"])
    while is_school:
        driver.execute_script("window.scrollTo(0, {});".format((i - 1) * cell_height))
        time.sleep(1)
        school_xpath = school_xpath_base.format("" if i == 1 else "[{0}]".format(i))
        school = driver.find_element_by_xpath(school_xpath).text
        if school in school_list:
            driver.find_element_by_xpath(school_xpath).click()
        i += 1
        school_xpath = school_xpath_base.format("" if i == 1 else "[{0}]".format(i))
        is_school = is_element_present(driver, By.XPATH, school_xpath)
    driver.find_element_by_id("btnNext").click()


def _change_start_date_and_period(driver):
    driver.find_element_by_id("dpStartDate").click()
    driver.find_element_by_xpath("//div[@id='ui-datepicker-div']/div/a[2]/span").click()
    driver.find_element_by_link_text("1").click()
    driver.find_element_by_id("lblPeriod1month").click()
    driver.find_element_by_id("btnHyoji").click()


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
    for k in len(weekend_and_holiday_list):
        # 朝
        date_xpath = date_xpath_base.format(k + 2, 2)
        count_with_chusen = driver.find_element_by_xpath(date_xpath).text
        if "抽選" in count_with_chusen:
            count_list_asa.append(_remove_chusen(count_with_chusen))
        else:
            count_list_asa.append('')
        # 昼A
        date_xpath = date_xpath_base.format(k + 2, 3)
        count_with_chusen = driver.find_element_by_xpath(date_xpath).text
        if "抽選" in count_with_chusen:
            count_list_hirua.append(_remove_chusen(count_with_chusen))
        else:
            count_list_hirua.append('')
        # 昼B
        date_xpath = date_xpath_base.format(k + 2, 4)
        count_with_chusen = driver.find_element_by_xpath(date_xpath).text
        if "抽選" in count_with_chusen:
            count_list_hirub.append(_remove_chusen(count_with_chusen))
        else:
            count_list_hirub.append('')
        # 夜
        date_xpath = date_xpath_base.format(k + 2, -1)
        count_with_chusen = driver.find_element_by_xpath(date_xpath).text
        if "抽選" in count_with_chusen:
            count_list_hirub.append(_remove_chusen(count_with_chusen))
        else:
            count_list_hirub.append('')
        div_height = int(driver.find_element_by_xpath(div_base.format(k + 2)).size["height"])
        driver.execute_script("window.scrollTo(0, {});".format((k + 1) * div_height))
    return count_list_asa, count_list_hirua, count_list_hirub, count_list_yoru


def _chooose_school_and_get_count_list(driver, school, weekend_and_holiday_list):
    print("school")
    print(school)
    displayed_school_xpath_prefix = "//div[@id='body']/div[2]/div[3]/div"
    displayed_school_xpath_suffix = "/h3/a"
    displayed_school_xpath_base = "//div[@id='body']/div[2]/div[3]/div[{0}]/h3/a"
    is_displayed_school = True
    j = 1
    displayed_school_xpath = displayed_school_xpath_base.format(j)
    div = "//div[@id='body']/div[2]/div[3]/div[1]"
    div_height = int(driver.find_element_by_xpath(div).size["height"])
    while is_displayed_school:
        displayed_school = driver.find_element_by_xpath(displayed_school_xpath).text
        print("displayed_school")
        print(displayed_school)
        print("j:{}".format(j))
        if displayed_school == school:
            for weekend_and_holiday in weekend_and_holiday_list:
                date = datetime.datetime.strptime(weekend_and_holiday, "%Y/%m/%d").day
                print("date:{}".format(date))
                if date >= 15:
                    xpath = "//div[@id='body']/div[2]/div[3]/div[{0}]".format(j)
                    driver.execute_script(
                        "document.evaluate({0},document,null,9,null).singleNodeValue.scrollLeft=document.evaluate({1},document,null,9,null).singleNodeValue.scrollWidth".format(
                            xpath, xpath))
                if j == 1:
                    driver.find_element_by_xpath(
                        "//div[@id='body']/div[2]/div[3]/div[{0}]/div[2]/table/tbody/tr/td[{1}]/label".format(j,
                                                                                                              int(
                                                                                                                  date) + 1)).click()
                else:
                    driver.find_element_by_xpath(
                        "//div[@id='body']/div[2]/div[3]/div[{0}]/div[1]/table/tbody/tr/td[{1}]/label".format(j,
                                                                                                              int(
                                                                                                                  date) + 1)).click()
            driver.find_element_by_link_text(u"次へ進む").click()
            count_list_asa, count_list_hirua, count_list_hirub, count_list_yoru = _get_count_list(driver,
                                                                                              weekend_and_holiday_list)
            driver.find_element_by_link_text(u"前に戻る").click()
            return count_list_asa, count_list_hirua, count_list_hirub, count_list_yoru
        driver.execute_script("window.scrollTo(0, {});".format(j * div_height))
        j += 1
        displayed_school_xpath = displayed_school_xpath_base.format(j)
        is_displayed_school = is_element_present(driver, By.XPATH, displayed_school_xpath)


def _remove_chusen(text):
    ken_start_index = text.index(u"(")
    ken_end_index = text.index(u")")
    return int(text[ken_start_index + 1:ken_end_index])


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


def is_element_present(driver, how, what):
    try:
        driver.find_element(by=how, value=what)
    except NoSuchElementException as e:
        return False
    return True
