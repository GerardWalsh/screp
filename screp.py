import time

from bs4 import BeautifulSoup
import pandas as pd
import joblib

import ipdb

from utils import load_yaml, setup_driver, find_total_ads, find_total_pages, get_ad_details

data = load_yaml("scrape_configs/autotrader_scrape_targets.yaml")
driver = setup_driver()


for manufacturer in data.keys():
    for model in data[manufacturer]:
        datas = []
        model_url = f"https://www.autotrader.co.za/cars-for-sale/{manufacturer}/{model}?pagenumber=1"
        driver.get(model_url)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        joblib.dump(soup, f'{model}')
        # soup = joblib.load("1seriessoup")
        pages = len(soup.find_all(*find_total_pages(soup, "autotrader")))
        for i in range(pages):
            # don't need to get the above data again
            if i != 0:
                print(f"Getting page {i} data")
                model_url = f"https://www.autotrader.co.za/cars-for-sale/{manufacturer}/{model}?pagenumber={i+1}"
                driver.get(model_url)
                time.sleep(5)
                soup = BeautifulSoup(driver.page_source, "html.parser")
    
            ad_count = int(soup.select(find_total_ads(soup, 'autotrader'))[0].text)
            for ad_soup in soup.select('[class^="b-result-tile__"]'):
                try:
                    datas.append(get_ad_details(ad_soup))
                except:
                    pass
        datas = pd.DataFrame(datas)
        import ipdb; ipdb.set_trace()