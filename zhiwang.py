# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import time 
import random
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from urllib.parse import urljoin

# params
theme = "抑郁症 针刺"
timeout = 8
papers_need = 20
try_again = 10

# env
chrome_options= webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument("window-size=1920,1080")
chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
browser = webdriver.Chrome(chrome_options=chrome_options)
browser.set_page_load_timeout(timeout)


# %%
### 
browser.get("https://kns.cnki.net/kns8/defaultresult/index")

# 传入关键字
WebDriverWait(browser, timeout).until(EC.presence_of_element_located((By.XPATH ,'//*[@id="txt_search"]'))).send_keys(theme)
WebDriverWait(browser, timeout).until(EC.presence_of_element_located((By.XPATH ,"/html/body/div[2]/div/div[2]/div[1]/input[2]"))).click()
time.sleep(timeout)

# %%
total_number = WebDriverWait(browser, timeout).until(EC.presence_of_element_located((By.XPATH ,'//*[@id="countPageDiv"]/span[1]/em'))).text
print("Find total papers: {}".format(total_number))
cur_page = WebDriverWait(browser, timeout).until(EC.presence_of_element_located((By.XPATH, '//*[@id="gridTable"]/div[2]/span[2]'))).text
print("Page {}".format(cur_page))

# %%
count = 0

import csv
f = open('results.csv','w',encoding='utf-8')
csv_writer = csv.writer(f)
csv_writer.writerow(["count","title","authors", "abstract"])

result = None 

while count < papers_need:

    papers_list = WebDriverWait(browser, timeout).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'fz14')))
    print(len(papers_list))
    index = 0
    while True:

        print(index, count)
        paper_link = papers_list[index]

        if count >= papers_need:
            break

        status = False

        try:
            paper_link.click()
            time.sleep(timeout)

            n = browser.window_handles
            browser.switch_to.window(n[-1])

            title =  WebDriverWait(browser, timeout).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[1]/div[3]/div/div/div[3]/div/h1'))).text
            authors = WebDriverWait(browser, timeout).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="authorpart"]/span')))
            authors = ",".join([ item.text for item in authors ])
            abstract = WebDriverWait(browser, timeout).until(EC.presence_of_element_located((By.XPATH, '//*[@id="ChDivSummary"]'))).text
            
            result = [str(count + 1), title, authors, abstract]

            print("[{}] {} {} {}".format(count + 1, title, authors, abstract))

            status = True

        except Exception as e:
            result = [str(count + 1), "", "", ""]
            print("[Fail] Crawl failure for No.{} paper : {}. Try again".format(count + 1, e))

            status = False
            try_again = try_again - 1   

        finally:
            n = browser.window_handles
            if len(n) > 1:
                browser.close()
                browser.switch_to.window(n[0])

            if status:
                csv_writer.writerow(result)
                count = count + 1
                index = index + 1
                try_again = 10
                if index >= 20:
                    break
            elif try_again < 0:
                count = count + 1
                index = index + 1
                try_again = 10
                if index >= 20:
                    break
            
    
    if count >= papers_need:
        break

    n = browser.window_handles
    if len(n) > 1:
        browser.close()
        browser.switch_to.window(n[0])
    
    next_page = int(cur_page) + 1
    print("Swich to {}".format(next_page))
    # 下一页
    while True:
        try:
            print("Try get cur_page")
            cur_page = WebDriverWait(browser, timeout).until(EC.presence_of_element_located((By.XPATH, '//*[@id="gridTable"]/div[2]/span[2]'))).text
            cur_page = int(cur_page)
            print(cur_page)
            if cur_page == next_page:
                break
            elif cur_page < next_page:
                WebDriverWait(browser, timeout).until(EC.presence_of_element_located((By.XPATH ,'//*[@id="PageNext"]'))).click()
                time.sleep(timeout)
            else:
                WebDriverWait(browser, timeout).until(EC.presence_of_element_located((By.XPATH ,'//*[@id="PagePrev"]'))).click()
                time.sleep(timeout)
        except Exception as e:
            print("[Fail] cannot switch to the next page : {}".format(e))
    
browser.close()
f.close()


