from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import yaml


def load_yaml(input_path: Path):
    with open(input_path) as pth:
        return yaml.safe_load(pth)


def setup_driver():
    opts = Options()
    opts.add_argument("--headless")
    return webdriver.Chrome(options=opts)


def find_total_pages(soup, site):
    total_ads_tags = {"autotrader": ("li", {"class": "e-page-number"})}
    return total_ads_tags[site]

def find_total_ads(soup, site):
    patterns = {"autotrader": '[class^="e-results-total__"]'}
    return patterns[site]

def get_ad_containers(soup, site):
    patterns = {"autotrader": '[class^="b-result-tile__"]'}
    return soup.select(patterns[site])

def get_ad_details(soup):
    data = {}
    for component in ['title', 'dealer', 'suburb', 'price']:
        # try:
        data[component] = soup.select(f'[class^="e-{component}__"]')[0].text.replace('\xa0', ' ')
        # except:
        #     import ipdb; ipdb.set_trace()
    for i, component in enumerate(['transmission', 'mileage']):
        data[component] = soup.select('[class^="e-summary-icon"]')[-1-i].text.replace('\xa0', ' ') #.replace("km", "").replace(" ", "")

    return pd.Series({
            **data
        })