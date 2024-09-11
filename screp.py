from datetime import datetime
import time

from bs4 import BeautifulSoup
import pandas as pd

from utils import (
    load_yaml,
    setup_driver,
    find_total_ads,
    find_total_pages,
    get_ad_details,
    insert_ads,
    get_soup
)
target_site = "autotrader"
url_patterns = {"autotrader": "https://www.autotrader.co.za/cars-for-sale/{manufacturer}/{model}?pagenumber=1"}
data = load_yaml(f"scrape_configs/{target_site}_scrape_targets.yaml")
driver = setup_driver()

model_url = url_patterns[target_site]
for manufacturer in data.keys():
    for model in data[manufacturer]:
        datas = []
        model_url = model_url.format(manufacturer, model)
        soup = get_soup(driver, model_url, pause=False)
        pages = len(soup.find_all(*find_total_pages(soup, "autotrader")))
        ad_count = int(soup.select(find_total_ads(soup, "autotrader"))[0].text)
        print(f"Found {ad_count} ads for {model}")
        for i in range(pages):
            if i != 0:
                print(f"Getting page {i+1} data")
                model_url = f"https://www.autotrader.co.za/cars-for-sale/{manufacturer}/{model}?pagenumber={i+1}"
                soup = get_soup(driver, model_url)

            for ad_soup in soup.select('[class^="b-result-tile__"]'):
                try:
                    datas.append(get_ad_details(ad_soup))
                except:
                    pass
        datas = pd.DataFrame(datas)
        datas["date_retrieved"] = str(datetime.now())
        insert_ads(db_name="listings", data=datas)
