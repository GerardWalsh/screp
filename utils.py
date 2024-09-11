from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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
