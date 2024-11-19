from pathlib import Path
import sqlite3
import time
from math import ceil
import re
import json
import requests
import os

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
        if (soup["resultType"] == 1) & ("price" in soup.keys()):
            data["ad_id"] = int(soup["listingId"])
            data["title"] = (
                str(soup["registrationYear"]) + " " + soup["makeModelLongVariant"]
            )
            data["dealer"] = soup["dealerName"]
            data["suburb"] = soup["dealerCityName"]
            data["price"] = str(soup["price"]).replace("\xa0", " ")
            data["transmission"] = soup["summaryIcons"][-1]["text"]
            data["mileage"] = soup["summaryIcons"][1]["text"].replace("\xa0", " ")
            data["image_url"] = soup["imageUrl"]
            data = pd.Series({**data})
            return data
    elif site == "wbc":
        data["ad_id"] = soup.find("div", class_="grid-card").get("id").split("-")[-1]
        data["title"] = soup.select('[class^="description"]')[0].text
        data["dealer"] = "wbc"
        data["suburb"] = soup.select('[class^="chip-text"]')[2].text
        price = soup.select('[class^="price-text"]')
        if price:
            data["price"] = price[0].text
        else:
            data["price"] = None

        data["transmission"] = "N/A"
        data["mileage"] = soup.select('[class^="chip-text"]')[0].text
        data["image_url"] = data["ad_id"]
    return pd.Series({**data})


def insert_ads(db_name: str, data: pd.DataFrame):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    cur.executemany(
        "INSERT INTO listings (ad_id, title, dealer, suburb, price, transmission, mileage, image_url, date_retrieved,  manufacturer, model) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
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
        script_tag = page_soup.find_all("script", text=re.compile(r"\breactRender\b"))[
            -3
        ]
        data = json.loads(script_tag.getText()[114:-31])
        return data["results"]["results"] + data["results"]["featuredTiles"]
    elif site == "wbc":
        return page_soup.select('[class^="m-2 grid-card-container"]')


def any_ads(page_soup, site):
    if site == "wbc":
        return not any(page_soup.select('[class^="no-results-message"]'))
    if site == "autotrader":
        return True


def pull_all_data(db_name):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    res = cur.execute("SELECT * FROM listings")
    df = pd.DataFrame(res.fetchall())
    df.columns = [
        "ad_id",
        "title",
        "dealer",
        "suburb",
        "price",
        "transmission",
        "mileage",
        "date_retrieved",
        "manufacturer",
        "model",
        "image_url",
    ]
    return df


def download_files_from_df(df, save_dir):
    for _, row in df.iterrows():
        url = row["image_url"]
        ad_id = row["ad_id"]
        try:
            if save_dir == "autotrader":
                filename = os.path.join(
                    save_dir,
                    str(ad_id).replace(".0", "") + ".jpg",
                )
            if save_dir == "wbc":
                url = (
                    "https://photos.webuycars.co.za/photobooth/"
                    + ad_id
                    + "/Images/"
                    + ad_id
                    + "0.webp"
                )
                filename = os.path.join(
                    save_dir,
                    ad_id + ".jpg",
                )

            response = requests.get(url)
            response.raise_for_status()

            with open(filename, "wb") as file:
                file.write(response.content)

        except requests.exceptions.RequestException as e:
            print(f"Failed to download {url}: {e}")
