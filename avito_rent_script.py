# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import pandas as pd
from bs4 import BeautifulSoup as bs
import re
from selenium import webdriver
import time
from tqdm import tqdm
from collections import defaultdict
import numpy as np
import sqlite3
conn = sqlite3.connect('Data\\rent.db')

# %%
url= 'https://www.avito.ru/moskva/kvartiry/sdam/na_dlitelnyy_srok-ASgBAgICAkSSA8gQ8AeQUg?cd=1&pmax=50000&proprofile=1&f=ASgBAQICAkSSA8gQ8AeQUgJAzAgkjFmOWay~DRSkxzU'
url_2 = 'https://www.avito.ru/moskva/kvartiry/sdam/na_dlitelnyy_srok/2-komnatnye-ASgBAQICAkSSA8gQ8AeQUgFAzAgUkFk?cd=1&pmax=50000&proprofile=1&f=ASgBAQICAkSSA8gQ8AeQUgJAzAgUkFmsvg0UpMc1'
#авито дает просмотреть только 100 страниц истории, поэтому разделение по отдельным запросам разные по количеству комнат квартир дает больший прирост информации.
urls = [url,url_2]
driver = webdriver.Chrome(r'C:\Users\AA2095\.wdm\drivers\chromedriver\win32\84.0.4147.30\chromedriver.exe')

# %%
for url in urls:
    driver.get(url)
    soap = bs(driver.page_source,'html.parser')
    pages = int(soap.findAll('span',{'class':'pagination-item-1WyVp'})[-2].text)
    for page in tqdm(range(pages),position=0):
        soap = bs(driver.page_source,'html.parser')
        d = defaultdict(list)
        block = soap.findAll('div',{'class':'item__line'})   
        for i in block:
            try:
                d['info'].append(i.find('span',{'itemprop':'name'}).getText(strip=True))
            except :
                d['info'].append('none')
            try:
                d['price'].append(i.find('span',{'itemprop':'offers'}).text.split('\n')[1])
            except :
                d['price'].append('none')
            try:
                d['adress'].append(i.find('span',{'class':'item-address__string'}).getText(strip=True))
            except :
                d['adress'].append('none')
            try:
                d['metro'].append(i.find('span',{'class':'item-address-georeferences-item__content'}).getText(strip=True))
            except:
                d['metro'].append('none')
            try:
                d['metro_dist'].append(i.find('span',{'class':'item-address-georeferences-item__after'}).text.split()[0])
            except:
                d['metro_dist'].append('none')
            try :
                d['url'].append('avito.ru'+i.a['href'])
            except:
                d['url'].append('none')
        df=pd.DataFrame(d).to_sql('rent_avito',conn,if_exists='append',index=False)
        df.price=df.price.str.replace('₽| ','').astype(int)
        df.m2=df.m2.str.replace('м²','').astype(float)
        try:
            driver.find_element_by_xpath('//span[@data-marker="pagination-button/next"]').click()
            time.sleep(np.random.randint(1,7))
            driver.find_element_by_xpath('//span[@data-marker="pagination-button/next"]')
        except:
            time.sleep(5)
            driver.refresh()
            time.sleep(2)
        
all_df = pd.read_sql_query('select * from rent_avito',conn)
all_df.drop_duplicates(inplace=True)
all_df.to_sql('rent_avito',conn,if_exists='replace',index=False)        
conn.close()
driver.close()

# %%
#df[['rooms','m2','floor']]=df['info'].str.split(',',expand=True)
#df[['floor','max_floors']]=df.floor.str.replace('эт.','').str.split('/',expand=True)
#df[['street','dom']]=df.adress.str.split(',',expand=True).iloc[:,:2]
#df['metro_dist']=df['metro_dist'].str.replace('none','0').apply(lambda x: float(x.replace(',','.'))*1000 if len(x.split(',')) ==2 else x).astype(float)
#df.price=df.price.str.replace('₽| ','').astype(int)
#df.m2=df.m2.str.replace('м²','').astype(float)



