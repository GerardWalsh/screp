import os
from pathlib import Path
import requests
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

def get_prop_listings(soup):
    return soup.find_all("div", {"class": "external-libraries-card-container"})

def get_total_pages(soup):
    return soup.find_all(class_="page-link")[-1].get('aria-label').split(" ")[-1]

def extract_prop_listing_urls(ads):
    listing_urls = set()
    for ad in ads:
        anchor_tags = ad.find_all('a')
        for anchor_tag in anchor_tags:
            href = anchor_tag.get('href')
            listing_urls.add(href)
    return listing_urls

def extract_prop_listing_info(driver):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    ads = get_prop_listings(soup)
    ad_urls = extract_prop_listing_urls(ads)
    return ads, ad_urls

opts = Options()
# opts.add_argument("--headless")
# opts.add_argument("--enable-javascript")
# opts.add_argument("--enable-cookies")
# opts.add_argument("--disable-notifications")
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
opts.add_argument(f"user-agent={user_agent}")
driver = webdriver.Chrome(options=opts)

# Initial hit
driver.get("https://www.cbre.com.au/properties/commercial-space?aspects=isLetting")
time.sleep(10) # not sure if neccessary at the moment

accept_button = driver.find_element(By.XPATH, '//button[contains(text(), "Accept")]')
accept_button.click()
timeout = 2
wait = WebDriverWait(driver, timeout)

# Get first page's html
soup = BeautifulSoup(driver.page_source, "html.parser")
ads = get_prop_listings(soup)
pages = get_total_pages(soup)
print(f"we have {len(ads)} ads, and {pages} pages.")

urls = set()
ad_urls = extract_prop_listing_urls(ads)
urls.update(ad_urls)

# Next page
next_button = driver.find_element(By.CSS_SELECTOR, '[aria-label="Next page"]')
action = ActionChains(driver)
action.move_to_element(next_button).click().perform()

# Wait for the new content to load
timeout = 15  # You can adjust the timeout value as needed
wait = WebDriverWait(driver, timeout)
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.external-libraries-card-container')))

# Now that the new content has loaded, you can parse the updated HTML
soup = BeautifulSoup(driver.page_source, "html.parser")
ads = get_prop_listings(soup)
ad_urls = extract_prop_listing_urls(ads)
urls.update(ad_urls)

import ipdb; ipdb.set_trace()
print(ads[0] == ads_2[0])
