#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 10:25:35 2024

@author: lichao

####
****very important


We need to develop a high performace Crawler:
    which could restart automatically in linux
"""

from bs4 import BeautifulSoup
from google.oauth2.service_account import Credentials
import pandas as pd
from pandas_gbq import to_gbq
from selenium import webdriver
from selenium.webdriver.common.by import By
import sys
import time

arg1 = int(sys.argv[1])
arg2 = int(sys.argv[2])

### credentials
credentials = Credentials.from_service_account_file('BQkey/key.json')
project_id = "quixotic-sol-387506"


txt_name = "Test-second.txt"

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = '/usr/bin/chromium-browser'  # Specify the path to chromedriver
chrome_options.add_argument('--headless') 

driver = webdriver.Chrome(options=chrome_options)

cnki = 'https://chn.oversea.cnki.net/kns/defaultresult/index'
driver.get(cnki)

first_time = True

with open('JournalNameList.txt', 'r') as file:
    journal_name_list_have = [line.strip() for line in file.readlines()]

journal_name_list = journal_name_list_have[arg1:arg1+arg2]

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
        for i in list(range(1,51)):
            try:
                article_element = f"/html/body/div[5]/div[2]/div[2]/div[2]/form/div/table/tbody/tr[{i}]/td[2]/a"
                driver.find_element(By.XPATH, article_element).click()
                time.sleep(30)
                
                record_list = []
                driver.switch_to.window(driver.window_handles[1])
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
                driver.close()
            except KeyboardInterrupt:
                print("Stop")
                break
            except Exception as e:
                print('fail!')
                time.sleep(10)
            
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(2)
            
            #record_df = pd.DataFrame(record_list)
            #record_df.columns = ['Title', 'Abstract', 'Keywords', 'Classification']
            #df.to_csv('ChineseDatabase.csv', encoding='utf-8')
            #to_gbq(record_df, destination_table = "REPT_data.REPT_TextMatcher_DataCrawler_RawData_Chinese",
            #       project_id=project_id, if_exists="append",
            #       credentials=credentials, progress_bar=False)
        #/html/body/div[5]/div[2]/div[2]/div[2]/form/div/div[2]/a[11]
        try:
            next_page = '/html/body/div[5]/div[2]/div[2]/div[2]/form/div/div[2]/a[11]'
            driver.find_element(By.XPATH, next_page).click()
        except:
            next_page = '/html/body/div[5]/div[2]/div[2]/div[2]/form/div/div[2]/a[9]'
            driver.find_element(By.XPATH, next_page).click()
        time.sleep(60)
    time.sleep(60)                       


"""
# bash
nohup sh -c '
for i in 52 53 54 55 56 57 58 59 
do
    python CNKI_Crawler_headless-readtxt-2.py "$i" 1 >> log3.txt
done
' &

"""            

