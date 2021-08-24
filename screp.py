import os
from pathlib import Path
import requests

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import seaborn as sns

opts = Options()
opts.add_argument("--headless")
chrome_driver_path = Path(os.getcwd()) / "chromedriver_linux64/chromedriver"

driver = webdriver.Chrome(options=opts, executable_path=chrome_driver_path)
driver.get("https://www.autotrader.co.za/cars-for-sale/toyota/86?sortorder=PriceLow")
soup = BeautifulSoup(driver.page_source, "html.parser")
pages = soup.find_all("li", {"class": "e-page-number"})

price = []
mileage = []
year = []

for page_number in range(1, len(pages) + 1):
    if page_number == 0:
        url = "https://www.autotrader.co.za/cars-for-sale/toyota/86?sortorder=PriceLow"
    else:
        url = f"https://www.autotrader.co.za/cars-for-sale/toyota/86?pagenumber={page_number}&sortorder=PriceLow"
    # driver.get(
    #     f"https://www.autotrader.co.za/cars-for-sale/toyota/86?pagenumber={page_number}&sortorder=PriceLow"
    # )

    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    meta = soup.find_all("span", {"class": "e-icons"})
    prices = soup.find_all("span", {"class": "e-price"})

    for ad in zip(prices, meta):
        try:
            price.append(int(ad[0].text.replace("R ", "").replace("\xa0", "")))
            year.append(int(ad[1].text[0:4]))
            mileage.append(int(ad[1].text[4:11].replace("\xa0", "")))
        except:
            pass


# driver.get(
#     "https://www.autotrader.co.za/cars-for-sale/toyota/86?pagenumber=2&sortorder=PriceLow"
# )

# soup = BeautifulSoup(driver.page_source, "html.parser")
# meta = soup.find_all("span", {"class": "e-icons"})
# prices = soup.find_all("span", {"class": "e-price"})

# for ad in zip(prices, meta):
#     try:
#         price.append(int(ad[0].text.replace("R ", "").replace("\xa0", "")))
#         year.append(int(ad[1].text[0:4]))
#         mileage.append(int(ad[1].text[4:11].replace("\xa0", "")))
#     except:
#         pass


sns.scatterplot(x=mileage, y=price, hue=year, palette="bright")
plt.xlabel("Mileage [km]")
plt.ylabel("Price [R]")
# plt.legend("Year")
plt.title("Price vs mileage for the Toyota 86, on Autotrader")
plt.show()

import ipdb

ipdb.set_trace()
