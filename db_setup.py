import sqlite3

con = sqlite3.connect("listing.db")
cur = con.cursor()

import ipdb; ipdb.set_trace()

cur.execute("DROP TABLE listings")
cur.execute("CREATE TABLE listings(ad_id, title, dealer, suburb, price, transmission, mileage, date_retrieved,  manufacturer, model)")