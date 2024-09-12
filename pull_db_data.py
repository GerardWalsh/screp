import pandas as pd
import sqlite3

con = sqlite3.connect("listing.db")
cur = con.cursor()
res = cur.execute("SELECT * FROM listings")
df = pd.DataFrame(res.fetchall())
df.columns = ["ad_id", "title", "dealer", "suburb", "price", "transmission", "mileage", "date_retrieved",  "manufacturer", "model"]

import ipdb; ipdb.set_trace()

df[df.model.eq('m4')].drop_duplicates(subset='ad_id')