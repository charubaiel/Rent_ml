# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import pandas as pd
from bs4 import BeautifulSoup as bs
import re
from selenium import webdriver
from webdriver_manager import chrome
import time
from tqdm import tqdm
from collections import defaultdict
import numpy as np


# %%
url= 'https://www.cian.ru/cat.php?currency=2&deal_type=rent&demolished_in_moscow_programm=0&engine_version=2&foot_min=15&is_first_floor=0&maxprice=50000&mebel_k=1&offer_type=flat&only_foot=2&region=1&repair%5B0%5D=3&rfgr=1&room1=1&room2=1&room9=1&type=4&wp=1'
d = defaultdict(list)
driver = webdriver.Chrome(chrome.ChromeDriverManager().install())
driver.get(url)
soap = bs(driver.page_source,'html.parser')


# %%
num_obj=int(re.sub(r'\D','',soap.find('div',{'data-name':'SummaryHeader'}).text))
pages = int(num_obj/30/1.7)


# %%
for page in tqdm(range(2,pages),position=0):
    if page >10:
        page=11  
    time.sleep(np.random.randint(4,7))
    block = soap.find('div',{'data-name':'Offers'}).findAll('div',{'class':'_93444fe79c--card--_yguQ'}) 
    for i in block:
        try:
            d['info'].append(i.find('div',{'class':'c6e8ba5398--subtitle--UTwbQ'}).text)
        except :
            d['info'].append('none')
        try:
            d['price'].append(i.find('div',{'class':'c6e8ba5398--header--1dF9r'}).text.split('/')[0])
        except :
            d['price'].append('none')
        try:
            d['adress'].append(i.find('span',{'itemprop':'name'})['content'])
        except :
            d['adress'].append('none')
        try:
            d['metro_dist'].append(i.find('div',{'class':'c6e8ba5398--remoteness--3bptF'}).text.split()[0])
        except:
            d['metro_dist'].append('none')
        try :
            d['url'].append(i.find('div',{'class':'c6e8ba5398--info--1fcZi'}).a['href'])
        except:
            d['url'].append('none')
        
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(4)
    driver.find_element_by_xpath(f'//*[@id="frontend-serp"]/div/div[5]/div/ul/li[{page}]/a').click()
    df=pd.DataFrame(d)



# %%
df=df.drop(df.query('info=="none"').index)
df[['rooms','m2','floor']]=df['info'].str.split(', ',expand=True)
df[['floor','max_floors']]=df.floor.str.replace('эт.','').str.split('/',expand=True)
df.max_floors=df.max_floors.apply(lambda x: re.sub(r'\D','',x))
df.metro_dist = df.metro_dist.astype(int)
df[['city','Area','district','metro','street','dom']]=df.adress.str.split(',',expand=True)
df.price=df.price.str.replace('₽| ','').astype(int)
df.m2=df.m2.str.replace(',','.').str.replace('м²','').astype(float)
df=df.drop(df.query('info=="none"').index)
df.to_csv(f'cian_rent_{time.localtime().tm_yday}.csv',index=False)



# %%



