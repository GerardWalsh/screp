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
driver.get("https://www.autotrader.co.za/cars-for-sale/bmw/m3?year=2007-to-2013")
soup = BeautifulSoup(driver.page_source, "html.parser")
pages = soup.find_all("li", {"class": "e-page-number"})

price = []
mileage = []
year = []

for page_number in range(1, len(pages) + 1):
    url = f"https://www.autotrader.co.za/cars-for-sale/bmw/m3?pagenumber={page_number}&year=2007-to-2013"
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    meta = soup.find_all("span", {"class": "e-icons"})
    prices = soup.find_all("span", {"class": "e-price"})

    for ad in zip(prices, meta):
        try:
            price.append(int(ad[0].text.replace("R ", "").replace("\xa0", "")))
            year.append(int(ad[1].text[0:4]))
            mileage.append(int(ad[1].text.split("km")[0][4:-1].replace("\xa0", "")))
        except:
            print("error appending")
            pass

sns.scatterplot(x=mileage, y=price, hue=year, palette="bright")
plt.xlabel("Mileage [km]")
plt.ylabel("Price [R]")
plt.title("Price vs mileage for the Toyota 86, on Autotrader")
plt.show()
