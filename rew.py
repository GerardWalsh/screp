import re
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd

import ipdb

import sqlite3

con = sqlite3.connect("tutorial.db")
cur = con.cursor()
cur.execute("SELECT * FROM ad").fetchall()


# from sqlalchemy import create_engine

# engine = create_engine("sqlite://", echo=False)
MODEL = "cayman"
MANUFACTURER = "porsche"
SUBMODEL = "gt4"
# URL = f"https://www.autotrader.co.za/cars-for-sale/{MANUFACTURER}/{MODEL}/{SUBMODEL}"
URL = "https://www.autotrader.co.za/cars-for-sale/porsche/718-cayman/gt4/search"
# ipdb.set_trace()
opts = Options()
opts.add_argument("--headless")

driver = webdriver.Chrome(options=opts)
driver.get(URL)
soup = BeautifulSoup(driver.page_source, "html.parser")
pages = soup.find_all("li", {"class": "e-page-number"})

# pages = [1]


def get_details(result_tile_soup):
    summary_data = result_tile_soup.find_all("li", {"class": "e-summary-icon"})
    mileage = (
        summary_data[1]
        .get_text(strip=True)
        .replace("\xa0", " ")
        .replace("km", "")
        .strip()
    ).replace(" ", "")
    gearbox = summary_data[2].get_text(strip=True).replace("\xa0", " ")
    return mileage, gearbox


def get_meta_data(result_tile_soup):
    ad_title = result_tile_soup.find("span", class_=re.compile(r"^e-title")).get_text(
        strip=True
    )
    year = ad_title[:4]
    return year, ad_title


def get_price(result_tile_soup):
    return (
        result_tile_soup.find("span", class_=re.compile(r"^e-price"))
        .find("span", recursive=False)
        .get_text(strip=True)
        .split("  ")[0]
        .replace("\xa0", " ")
        .replace("R", "")
        .strip()
        .replace(" ", "")
    )


def get_link(result_tile_soup):
    return (
        result_tile_soup.find("a")["href"]
        .split("?")[0]
        .replace("/car-for-sale", "car-for-sale")
    )


def build_results_df(data):
    df = pd.DataFrame(data, columns=["link", "year", "mileage", "price", "gearbox"])
    df["mileage"] = df["mileage"].astype(int)
    df["price"] = df["price"].astype(int)
    return df


def get_ad_data(result_tile):
    # ipdb.set_trace()
    mileage, gearbox = get_details(result_tile)
    year, title = get_meta_data(result_tile)
    price = get_price(result_tile)
    link = get_link(result_tile)
    dealer_name = get_dealer_name(result_tile)
    dealer_location = get_dealer_location(result_tile)
    return [link, title, year, mileage, price, gearbox, dealer_name, dealer_location]


def dump_html(soup, page_number):
    pretty_html = soup.prettify()
    with open(
        f"{datetime.now()}_page_{page_number}_output.html", "w", encoding="utf-8"
    ) as file:
        file.write(pretty_html)


def get_dealer_name(result_tile_soup):
    return result_tile_soup.find("span", class_=re.compile(r"^e-dealer__")).get_text(
        strip=True
    )


def get_dealer_location(result_tile_soup):
    return result_tile_soup.find("span", class_=re.compile(r"^e-suburb__")).get_text(
        strip=True
    )


def read_html(path):
    # Open and read the HTML file
    with open(path, "r", encoding="utf-8") as file:
        html_content = file.read()

    # Parse HTML content using BeautifulSoup
    return BeautifulSoup(html_content, "html.parser")


data = []
print(f"Got {len(pages)} pages of results . . .")
# ipdb.set_trace()
for page_number in range(1, len(pages) + 1):
    # url = f"https://www.autotrader.co.za/cars-for-sale/bmw/m3?pagenumber={page_number}&year=2007-to-2013"
    # url = URL + f"?pagenumber={page_number}"
    url = URL
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    # soup = read_html("2024-06-02 11:50:42.612901_page_1_output.html")
    dump_html(soup, page_number)

    featured_ads = soup.find_all("div", {"class": "e-featured-tile-container"})
    for result_tile in featured_ads:
        # ipdb.set_trace()
        try:
            data.append(get_ad_data(result_tile) + ["featured"])
        except:
            pass
    # ipdb.set_trace()
    normal_ads = soup.find_all("div", class_=re.compile(r"^b-result-tile"))
    for result_tile in normal_ads:
        try:
            # ipdb.set_trace()
            data.append(get_ad_data(result_tile) + ["standard"])
        except:
            pass
ipdb.set_trace()
df = pd.DataFrame(
    data,
    columns=[
        "link",
        "title",
        "year",
        "mileage",
        "price",
        "gearbox",
        "dealer_name",
        "dealer_location",
        "ad_type",
    ],
)
df["mileage"] = df["mileage"].astype(int)
df["model"] = "cayman gt4"
df["manufacturer"] = "porsche"

ipdb.set_trace()
db_data = pd.DataFrame(
    cur.execute("Select * from ads").fetchall(),
    # columns=["link", "year", "mileage", "price", "gearbox"],
)
# ipdb.set_trace()

# new_data = df[~df["link"].isin(db_data[0])]
df.to_sql("ads", con, index=False, if_exists="append")
# ipdb.set_trace()
# con.close()

# TODO: Capture first 3 premium ads
# TODO: Save images
# TODO: write failures to disk?
# TODO: Capture dealer info - done
# TODO: Capture location info - done
