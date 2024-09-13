from pathlib import Path
import sqlite3
import time
from math import ceil

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
    if site == "autotrader":
        return int(soup.select('[class^="e-page-number"]')[-1].text)
    elif site == "wbc":
        if any(soup.find_all("ul", class_="pagination")):
            return ceil(
                int(
                    [
                        x.text
                        for x in soup.find_all("div", class_="text-center")
                        if "Showing 1" in x.text
                    ][0]
                    .split("of ")[-1]
                    .replace(")", "")
                )
                / 23
            )
        else:
            return 1


def find_total_ads(soup, site):
    if site == "autotrader":
        total = int(soup.select('[class^="e-results-total__"]')[0].text)
    elif site == "wbc":
        if any(soup.find_all("ul", class_="pagination")):
            return int(
                [
                    x.text
                    for x in soup.find_all("div", class_="text-center")
                    if "Showing 1" in x.text
                ][0]
                .split("of ")[-1]
                .replace(")", "")
            )
        else:
            return 1
    return total


def get_ad_containers(soup, site):
    patterns = {"autotrader": '[class^="b-result-tile__"]'}
    return soup.select(patterns[site])


def get_ad_details(soup, site):
    data = {}
    if site == "autotrader":
        data["ad_id"] = soup.find("a").get("href").split("?")[0].split("/")[-1]
        for component in ["title", "dealer", "suburb", "price"]:
            data[component] = soup.select(f'[class^="e-{component}__"]')[
                0
            ].text.replace("\xa0", " ")
        for i, component in enumerate(["transmission", "mileage"]):
            data[component] = soup.select('[class^="e-summary-icon"]')[
                -1 - i
            ].text.replace("\xa0", " ")
    elif site == "wbc":
        data["ad_id"] = soup.find("div", class_="grid-card").get("id").split("-")[-1]
        data["title"] = soup.select('[class^="description"]')[0].text
        data["dealer"] = "wbc"
        data["suburb"] = soup.select('[class^="chip-text"]')[2].text
        data["price"] = soup.select('[class^="price-text"]')[0].text

        data["transmission"] = "N/A"
        data["mileage"] = soup.select('[class^="chip-text"]')[0].text

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
    elif site == "wbc":
        return page_soup.select('[class^="m-2 grid-card-container"]')


def any_ads(page_soup, site):
    if site == "wbc":
        return not any(page_soup.select('[class^="no-results-message"]'))
    if site == "autotrader":
        return True
