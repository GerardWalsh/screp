import os
from pathlib import Path
import requests

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

opts = Options()
opts.add_argument("--headless")
chrome_driver_path = Path(os.getcwd()) / "chromedriver_linux64/chromedriver"

driver = webdriver.Chrome(options=opts, executable_path=chrome_driver_path)
driver.get("https://www.webuycars.co.za/buy-a-car?q=86")

soup = BeautifulSoup(driver.page_source, "html.parser")
eight_sixes = soup.find_all("div", {"class": "filter-item-media"})
print(f"we Have {len(eight_sixes)} examples")

first_love = eight_sixes[0]
first_loves_address = first_love.select_one("a")["href"]
we_buy_cars_home_prefix = "https://www.webuycars.co.za"

url = we_buy_cars_home_prefix + first_loves_address
response = requests.get(url)
new_soup = BeautifulSoup(driver.page_source, "html.parser")
price = new_soup.find("div", {"class": "d-flex align-items-center mr-1"}).get_text().replace("\xa0", "")

print(f'First GT86 costs {price}')
