from datetime import datetime

import pandas as pd

from utils import (
    load_yaml,
    setup_driver,
    find_total_ads,
    find_total_pages,
    get_ad_details,
    insert_ads,
    get_soup,
    get_all_page_ads,
    any_ads,
)

target_site = input("autotrader or wbc: ")
url_patterns = {
    "autotrader": "https://www.autotrader.co.za/cars-for-sale/{}/{}?pagenumber={}",
    "wbc": 'https://www.webuycars.co.za/buy-a-car?Make=["{}"]&Model=["{}"]&page={}',
}
data = load_yaml(f"scrape_configs/{target_site}_scrape_targets.yaml")
driver = setup_driver()

model_url = url_patterns[target_site]
for manufacturer in data.keys():
    for model in data[manufacturer]:
        datas = []
        model_url = url_patterns[target_site].format(manufacturer, model, 1)
        print(f"Scraping {model_url}")
        soup = get_soup(driver, model_url)
        if not any_ads(soup, target_site):
            print(f"No ads for {model} at {model_url}")
            continue
        # ad_count = find_total_ads(soup, target_site)
        ad_count = 999
        pages = find_total_pages(soup, target_site)
        print(f"Found {pages} pages and {ad_count} ads for {model}.")
        for i in range(pages):
            if i != 0:
                print(f"Getting page {i+1} data")
                model_url = url_patterns[target_site].format(manufacturer, model, i + 1)
                soup = get_soup(driver, model_url)
            for ad_soup in get_all_page_ads(soup, target_site):
                try:
                    datas.append(get_ad_details(ad_soup, target_site))
                except:
                    # import ipdb; ipdb.set_trace()
                    pass
        datas = pd.DataFrame(datas)
        datas["date_retrieved"] = str(datetime.now())
        datas["manufacturer"] = manufacturer
        datas["model"] = model
        insert_ads(db_name="listing.db", data=datas)

driver.close()
