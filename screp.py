import time
from datetime import datetime

from bs4 import BeautifulSoup
import pandas as pd
import sqlite3

import ipdb

from utils import load_yaml, setup_driver, find_total_ads, find_total_pages, get_ad_details

data = load_yaml("scrape_configs/autotrader_scrape_targets.yaml")
driver = setup_driver()
con = sqlite3.connect("listing.db")
cur = con.cursor()


for manufacturer in data.keys():
    for model in data[manufacturer]:
        datas = []
        model_url = f"https://www.autotrader.co.za/cars-for-sale/{manufacturer}/{model}?pagenumber=1"
        driver.get(model_url)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        pages = len(soup.find_all(*find_total_pages(soup, "autotrader")))
        ad_count = int(soup.select(find_total_ads(soup, 'autotrader'))[0].text)
        print(f"Found {ad_count} ads for {model}")
        for i in range(pages):
            if i != 0:
                print(f"Getting page {i+1} data")
                model_url = f"https://www.autotrader.co.za/cars-for-sale/{manufacturer}/{model}?pagenumber={i+1}"
                driver.get(model_url)
                time.sleep(5)
                soup = BeautifulSoup(driver.page_source, "html.parser")
    
            for ad_soup in soup.select('[class^="b-result-tile__"]'):
                try:
                    datas.append(get_ad_details(ad_soup))
                except:
                    pass
        datas = pd.DataFrame(datas)
        datas['date_retrieved'] = str(datetime.now())

        cur.executemany("INSERT INTO listings VALUES(?, ?, ?, ?, ?, ?, ?)", datas.values.tolist())
        con.commit()
