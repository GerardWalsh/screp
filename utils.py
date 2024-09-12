from pathlib import Path
import sqlite3
import time

from bs4 import BeautifulSoup
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
    total_ads_tags = {"autotrader": '[class^="e-page-number"]'}
    return total_ads_tags[site]


def find_total_ads(soup, site):
    patterns = {"autotrader": '[class^="e-results-total__"]'}
    return patterns[site]


def get_ad_containers(soup, site):
    patterns = {"autotrader": '[class^="b-result-tile__"]'}
    return soup.select(patterns[site])


def get_ad_details(soup):
    data = {}
    data["ad_id"] = soup.find("a").get("href").split("?")[0].split("/")[-1]
    for component in ["title", "dealer", "suburb", "price"]:
        data[component] = soup.select(f'[class^="e-{component}__"]')[0].text.replace(
            "\xa0", " "
        )
    for i, component in enumerate(["transmission", "mileage"]):
        data[component] = soup.select('[class^="e-summary-icon"]')[-1 - i].text.replace(
            "\xa0", " "
        )  # .replace("km", "").replace(" ", "")

    return pd.Series({**data})


def insert_ads(db_name: str, data: pd.DataFrame):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    cur.executemany(
        "INSERT INTO listings VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        data.values.tolist(),
    )
    con.commit()


def get_soup(driver, url, pause=True):
    driver.get(url)
    if pause:
        time.sleep(5)
    return BeautifulSoup(driver.page_source, "html.parser")


def get_all_page_ads(page_soup, site):
    if site == "autotrader":
        return page_soup.select('[class^="b-result-tile__"]')
