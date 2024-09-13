# screp

"_That's nice honey._"

![Image](rickyrick.png)

## You'll need

- A chromewebdriver, that you can get [here](https://chromedriver.chromium.org/downloads). Extract into the root directory of the repo.
- To install the [requirements](./requirements.txt).


## TODO (mvp)

* build URL from yaml for model [x]
* iterate over pages per model [x]
* sleep per page request, to go easy on the servers [x]
* get each ad container [x]
* parse out: [x]
* * title, price, mileage, location, dealer info, transmission
* handle dud advert []
* pull out ad_id [x]
* pull images from page, store with ad_id []
* * bit harder for autotrader, rendered dynamically?
* test data matches expectations []
* insert page data into DB [x]
* page count doesn't work for lots of pages (model w/ tons of ads) [x]
* add a test to test if all ads on page pass []
* add webuycars scraping [x]
* add cars.co.za scraping []
* check for duplicates in important places 
* * ad_id

## TODO (global picture)

* scheduling
* separate steps for extracting, transforming & loading
* monitoring
* shipping to cloud service (or not local machine)
