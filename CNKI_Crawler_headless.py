#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 10:25:35 2024

@author: lichao
"""

from bs4 import BeautifulSoup
from google.oauth2.service_account import Credentials
import pandas as pd
from pandas_gbq import to_gbq
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

### credentials
credentials = Credentials.from_service_account_file('BQkey/key.json')
project_id = "quixotic-sol-387506"


txt_name = "Test.txt"

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = '/usr/bin/chromium-browser'  # Specify the path to chromedriver
chrome_options.add_argument('--headless') 

driver = webdriver.Chrome(options=chrome_options)

cnki = 'https://chn.oversea.cnki.net/kns/defaultresult/index'
driver.get(cnki)

first_time = True

journal_name_list = [ '东南大学学报(哲学社会科学版)', '东南学术', 
                     '东南亚研究', '东岳论丛',
                     '法律科学(西北政法大学学报)', '福建论坛(人文社会科学版)', 
                     '福建师范大学学报(哲学社会科学版)', '妇女研究论丛']



for journal_name in journal_name_list:
    #select to use resource
    selection_element = '/html/body/div[4]/div/div[2]/div[1]/div[1]/div[1]/i'
    driver.find_element(By.XPATH, selection_element).click()
    time.sleep(1)
    resource_element = '/html/body/div[4]/div/div[2]/div[1]/div[1]/div[2]/ul/li[14]'
    driver.find_element(By.XPATH, resource_element).click()
    time.sleep(1)
    
    search_box = "/html/body/div[4]/div/div[2]/div[1]/input[1]"
    search_box_element = driver.find_element(By.XPATH, search_box)
    
    search_box_element.clear()
    search_box_element.send_keys(journal_name)
    time.sleep(1)
    print(journal_name)
    
    search_bottom = "/html/body/div[4]/div/div[2]/div[1]/input[2]"
    driver.find_element(By.XPATH, search_bottom).click()
    time.sleep(20)
    
    ### loop
    
    ### first_time setting
    if first_time:
        first_time = False
        time_ranking = '/html/body/div[5]/div[2]/div[2]/div[2]/form/div/div[1]/div[2]/div[3]/ul/li[2]'
        driver.find_element(By.XPATH, time_ranking).click()
        time.sleep(60)
        number_page = '/html/body/div[5]/div[2]/div[2]/div[2]/form/div/div[1]/div[2]/div[2]/div/div/div/i'
        driver.find_element(By.XPATH, number_page).click()
        time.sleep(1)
        item_50 = '/html/body/div[5]/div[2]/div[2]/div[2]/form/div/div[1]/div[2]/div[2]/div/div/ul/li[3]/a'
        driver.find_element(By.XPATH, item_50).click()
        time.sleep(30)
    
    
    for j in range(30):
        for i in list(range(1,51,2)):
            article_element = f"/html/body/div[5]/div[2]/div[2]/div[2]/form/div/table/tbody/tr[{i}]/td[2]/a"
            driver.find_element(By.XPATH, article_element).click()
            time.sleep(1)
            article_element = f"/html/body/div[5]/div[2]/div[2]/div[2]/form/div/table/tbody/tr[{i+1}]/td[2]/a"
            driver.find_element(By.XPATH, article_element).click()
            time.sleep(1)
            time.sleep(50)
            
            record_list = []
            for windows in list(range(2)):
                driver.switch_to.window(driver.window_handles[1])
                try:
                    page_html = driver.page_source
                    soup = BeautifulSoup(page_html, "html.parser")
                    
                    wx_tit = soup.find("div", class_="wx-tit")
                    try:
                        h1_text = wx_tit.find("h1").get_text()
                    except KeyboardInterrupt:
                        print("Stop")
                        break
                    except Exception as e:
                        h1_text = ''
                    
                    try:
                        abs_text = soup.find("span", class_="abstract-text").get_text()
                    except KeyboardInterrupt:
                        print("Stop")
                        break
                    except Exception as e:
                        abs_text = ''
                    
                    try:
                        kw_p_list  = soup.find_all("p", class_="keywords")
                        keyword_texts = []
                        for kw_p in kw_p_list:
                            keyword_links = kw_p.find_all("a", onclick=True)
                            for link in keyword_links:
                                keyword_texts.append(link.get_text(strip=True))
                        keywords_text = " ".join(keyword_texts)
                    except KeyboardInterrupt:
                        print("Stop")
                        break
                    except Exception as e:
                        keywords_text = ''
                    
                    classification = soup.find_all("li", class_="top-space")
                    classification_number = ''
                    for html_element in classification:
                        if html_element and "分类号" in str(html_element):
                            p_element = html_element.find("p")
                            if p_element:
                                classification_number = p_element.get_text()
                                
                    row = [h1_text, abs_text, keywords_text, classification_number]
                    print(h1_text)
                    record_list.append(row)
                    with open(txt_name, 'a', encoding='utf-8') as file:
                        for items in row:
                            file.write(items + ':;:')
                        file.write('\n')
                except KeyboardInterrupt:
                    print("Stop")
                    break
                except Exception as e:
                    print('fail!')
                driver.close()
            
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(2)
            
            record_df = pd.DataFrame(record_list)
            record_df.columns = ['Title', 'Abstract', 'Keywords', 'Classification']
            #df.to_csv('ChineseDatabase.csv', encoding='utf-8')
            to_gbq(record_df, destination_table = "REPT_data.REPT_TextMatcher_DataCrawler_RawData_Chinese",
                   project_id=project_id, if_exists="append",
                   credentials=credentials, progress_bar=True)
        #/html/body/div[5]/div[2]/div[2]/div[2]/form/div/div[2]/a[11]
        try:
            next_page = '/html/body/div[5]/div[2]/div[2]/div[2]/form/div/div[2]/a[11]'
            driver.find_element(By.XPATH, next_page).click()
        except:
            next_page = '/html/body/div[5]/div[2]/div[2]/div[2]/form/div/div[2]/a[9]'
            driver.find_element(By.XPATH, next_page).click()
        time.sleep(30)
    time.sleep(60)                       
            
            
"""
# crawler-1
journal_name_list = [ '当代经济科学', '地理科学进展', '法商研究', '法学论坛',
                     '法学评论', '当代传播', '出版发行研究', '法制与社会发展']
# crawler-2
journal_name_list = [ '安徽大学学报(哲学社会科学版)', '北京大学学报(哲学社会科学版)', 
                     '北京电影学院学报', '北京工商大学学报(社会科学版)',
                     '北京工业大学学报(社会科学版)', '北京联合大学学报(人文社会科学版)', 
                     '北京社会科学', '北京师范大学学报(社会科学版)']

# crawler-3
journal_name_list = [ '北京体育大学学报', '北京行政学院学报', 
                     '比较法研究', '比较教育研究',
                     '重庆大学学报(社会科学版)', '大连理工大学学报(社会科学版)', 
                     '东北大学学报(社会科学版)', '东北师大学报(哲学社会科学版)']
# crawler-4
journal_name_list = [ '东南大学学报(哲学社会科学版)', '东南学术', 
                     '东南亚研究', '东岳论丛',
                     '法律科学(西北政法大学学报)', '福建论坛(人文社会科学版)', 
                     '福建师范大学学报(哲学社会科学版)', '妇女研究论丛']

### prepared
# crawler-1
journal_name_list = [ '复旦教育论坛', '复旦学报(社会科学版)', '干旱区资源与环境', '甘肃社会科学',
                     '甘肃行政学院学报', '高等工程教育研究', '高等教育研究', '高校教育管理']
# crawler-2
journal_name_list = [ '公共行政评论', '管理工程学报', 
                     '管理评论', '管理世界',
                     '管理学报', '管理学刊', 
                     '广东财经大学学报', '广东社会科学']

# crawler-3
journal_name_list = [ '广西大学学报(哲学社会科学版)', '广西民族大学学报(哲学社会科学版)', 
                     '广西民族研究', '贵州财经大学学报',
                     '贵州民族研究', '贵州社会科学', 
                     '国际观察', '国际金融研究']
# crawler-4
journal_name_list = [ '国际经济评论', '国际经贸探索', 
                     '国际贸易', '国际商务(对外经济贸易大学学报)',
                     '国际新闻界', '国际展望', 
                     '国际政治研究', '国家教育行政学院学报']

"""          
    
    
    
