from bs4 import BeautifulSoup
import pandas as pd
import regex as re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

txt_name = "ChineseArticleData.txt"

driver = webdriver.Chrome()

cnki = 'https://chn.oversea.cnki.net/kns/defaultresult/index'
driver.get(cnki)

search_box = "/html/body/div[4]/div/div[2]/div[1]/input[1]"
search_box_element = driver.find_element(By.XPATH, search_box)

search_box_element.send_keys("经济地理")
time.sleep(1)

search_bottom = "/html/body/div[4]/div/div[2]/div[1]/input[2]"
driver.find_element(By.XPATH, search_bottom).click()

df_row = []

for j in range(120):
    for i in list(range(1,51)):
        article_element = f"/html/body/div[5]/div[2]/div[2]/div[2]/form/div/table/tbody/tr[{i}]/td[2]/a"
        #/html/body/div[5]/div[2]/div[2]/div[2]/form/div/table/tbody/tr[1]/td[2]/a
        driver.find_element(By.XPATH, article_element).click()
        time.sleep(30)
        
        driver.switch_to.window(driver.window_handles[1])
        try:
            page_html = driver.page_source
        except:
            time.sleep(30)
            page_html = driver.page_source
        soup = BeautifulSoup(page_html, "html.parser")
        
        wx_tit = soup.find("div", class_="wx-tit")
        try:
            h1_text = wx_tit.find("h1").get_text()
        except:
            h1_text = ''
        
        try:
            abs_text = soup.find("span", class_="abstract-text").get_text()
        except:
            abs_text = ''
        
        try:
            kw_p_list  = soup.find_all("p", class_="keywords")
            keyword_texts = []
            for kw_p in kw_p_list:
                keyword_links = kw_p.find_all("a", onclick=True)
                for link in keyword_links:
                    keyword_texts.append(link.get_text(strip=True))
            keywords_text = " ".join(keyword_texts)
        except:
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
        df_row.append(row)
            
        driver.close()
        
        driver.switch_to.window(driver.window_handles[0])
        time.sleep(2)
        
        with open(txt_name, 'a', encoding='utf-8') as file:
            for items in row:
                file.write(items + ':;:')
            file.write('\n')
        
    df = pd.DataFrame(df_row)
    #df.to_csv('ChineseDatabase.csv', encoding='utf-8')
    
    next_page = '/html/body/div[5]/div[2]/div[2]/div[2]/form/div/div[2]/a[9]'
    driver.find_element(By.XPATH, next_page).click()
    time.sleep(30)





