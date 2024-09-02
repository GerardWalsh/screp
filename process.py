import pandas as pd
from data_utils import get_all_data
from datetime import timedelta, datetime


model_gen_year_mapping = {
    "911": {
        "996": [1996, 2005],
        "997": [2006, 2013],
        "991": [2013, 2018],
        "992": [2018, 2024],
    },
    "m3": {
        "e36": [1990, 2000],
        "e46": [2000, 2006],
        "e9x": [2007, 2013],
        "f80": [2014, 2019],
        "g80": [2020, 2024],
    },
    "s2000": {"ap1": [1999, 2003], "ap2": [2003, 2009]},
    "jimny": {
        "3rd gen - JB43": [1998, 2018],
        "4th gen - JB74": [2019, 2024],
    },
    "land-cruiser-prado": {
        "2nd gen": [1196, 2002],
        "3rd gen": [2002, 2009],
        "4th gen": [2009, 2023],
        "5th gen": [2024, 2024],
    },
}


def get_the_data(group):
    year = group["year"].unique()[0]
    model = group["model"].unique()[0]
    manu = group["manufacturer"].unique()[0]
    min = int(group["price"].fillna(999).min())
    max = int(group["price"].fillna(999).max())
    link = group["link"].unique()[0]
    time_online = (
        pd.to_datetime(group["scrape_time"]).max()
        - pd.to_datetime(group["scrape_time"]).min()
    )
    sold = pd.to_datetime(group["scrape_time"].fillna("").max()) < (
        datetime.now() - timedelta(days=1)
    )
    site = group["site"].unique()[0]
    last_seen = pd.to_datetime(group["scrape_time"]).max()
    date_scraped = pd.to_datetime(group["scrape_time"]).min()
    title = group["title"].unique().tolist()[0]
    generation = group["generation"].unique().tolist()[0]
    image_url = group["image_url"].fillna("no image").unique().tolist()[-1]
    return pd.Series(
        {
            "manufacturer": manu,
            "model": model,
            "generation": generation,
            "year": year,
            "min_price": min,
            "max_price": max,
            "time_online": time_online,
            "last_seen": last_seen,
            "date_listed": date_scraped,
            "mileage": group["mileage"].fillna(999).astype(int).unique().tolist()[0],
            "sold": sold,
            "site": site,
            "title": title,
            "link": link,
            "image_url": image_url,
        }
    )


df = get_all_data()
df = df.drop(columns=["tite", "ad_type"])
df.model = df.model.fillna("").str.lower()
df["submodel"] = ""
df["generation"] = ""
df.year = pd.to_numeric(df.year, errors="coerce")

# cleanup
df = df[
    ~df.scrape_time.isin(
        [
            "2024-06-16 15:40:49.219883",
            "2024-06-21 09:11:33.916770",
            "2024-06-16 15:38:57.234642",
            "2024-06-18 07:27:59.075133",
            "2024-06-18 14:43:45.121460",
            "2024-07-13 07:57:19.993946",
            "2024-06-19 09:05:08.896269",
            "2024-06-19 15:17:39.997675",
            "2024-07-12 08:51:46.790416",
            "2024-07-13 07:59:42.217412",
            "2024-07-13 08:00:32.816607",
            "2024-06-20 09:06:34.454985",
            "2024-06-20 11:30:55.895534",
            "2024-07-13 08:00:32.816607",
        ]
    )
]


df.loc[df.model.eq("m2") & df.link.str.contains("m3"), "model"] = "m3"
df.loc[df.model.eq("m3") & df.title.fillna("").str.contains("M4"), "model"] = "m4"

df.loc[df.scrape_time.eq("2024-06-05 07:49:52.904515"), "manufacturer"] = "Porsche"
df.loc[df.scrape_time.eq("2024-06-05 07:49:52.904515"), "model"] = "Cayenne"

df.loc[df.scrape_time.eq("2024-06-05 07:50:13.181581"), "manufacturer"] = "Mercedes-Benz"
df.loc[df.scrape_time.eq("2024-06-05 07:50:13.181581"), "model"] = "A Class"

df.loc[df.scrape_time.eq("2024-06-05 07:51:04.309474"), "manufacturer"] = "BMW"
df.loc[df.scrape_time.eq("2024-06-05 07:51:04.309474"), "model"] = "3 series"

df.loc[df.scrape_time.eq("2024-06-05 21:23:15.260074"), "model"] = "86"
df.loc[df.scrape_time.eq("2024-06-05 21:23:15.260074"), "manufacturer"] = "Toyota"

df.loc[df.scrape_time.eq("2024-06-05 07:48:26.940071"), "manufacturer"] = "honda"
df.loc[df.scrape_time.eq("2024-06-05 07:48:26.940071"), "model"] = "s2000"

df.loc[df.model.eq("1-series"), "model"] = "1 series"
df.loc[df.model.eq("2-series"), "model"] = "2 series"
df.loc[df.model.eq("3-series"), "model"] = "3 series"

df.loc[
    df.title.str.lower().str.contains("yaris") & df.title.str.lower().str.contains("gr"),
    "model",
] = "gr yaris"

df.loc[
    df.title.str.lower().str.contains("corolla")
    & df.title.str.lower().str.contains("gr"),
    "model",
] = "gr corolla"

# df.loc[df.model.eq('m2'), 'submodel'] = 'm2'
# df.loc[df.model.eq('m2'), 'model'] = '2 series'

# df.loc[df.model.eq('m3'), 'submodel'] = 'm3'
# df.loc[df.model.eq('m3'), 'model'] = '3 series'

# df.loc[df.model.eq('m5'), 'submodel'] = 'm5'
# df.loc[df.model.eq('m5'), 'model'] = '5 series'

# TODO: add c63?

df.loc[
    df.title.str.lower().str.contains("911") & df.title.str.lower().str.contains("gt2"),
    "model",
] = "911 gt2"
df.loc[
    df.title.str.lower().str.contains("911") & df.title.str.lower().str.contains("gt3"),
    "model",
] = "911 gt3"

df.loc[df.model.eq("prado"), "model"] = "land-cruiser-prado"
df.loc[df.manufacturer.eq("alfa romeo"), "manufacturer"] = "alfa-romeo"
df.loc[df.model.eq("c-class/c63/search"), "model"] = "c class"

df.loc[df.site.eq("webuycars"), "image_url"] = (
    "https://photos.webuycars.co.za/photobooth/"
    + df.loc[df.site.eq("webuycars")].link
    + "/Images/"
    + df.loc[df.site.eq("webuycars")].link
    + "0.webp"
)

df.model = df.model.fillna("").str.lower()
df.manufacturer = df.manufacturer.fillna("").str.lower()


for model in model_gen_year_mapping.keys():
    for gen in model_gen_year_mapping[model]:
        yr_min, yr_max = model_gen_year_mapping[model][gen]
        df.loc[df.year.between(yr_min, yr_max) & (df.model == model), "generation"] = gen


df.loc[
    ~df[["model", "title"]].fillna("").apply(lambda x: x.model in x.title.lower(), axis=1)
].model.unique()


df.loc[df.link.str.contains("car-for-sale"), "link"] = (
    "https://www.autotrader.co.za/" + df.loc[df.link.str.contains("car-for-sale"), "link"]
)


df.loc[df.link.str.contains("car-for-sale"), "link"] = df.loc[
    df.link.str.contains("car-for-sale"), "link"
].str.replace("//car", "/car")
df.loc[df.link.str.contains("car-for-sale"), "link"]


df.loc[df.manufacturer.eq("alfa romeo"), "manufacturer"] = "alfa-romeo"
df.to_csv("data.csv")

df = pd.read_csv("data.csv")
for col in ["year", "price", "mileage"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(999).astype(int)

df = df.groupby("link").apply(get_the_data).reset_index(drop=True)
df.to_csv("frontend_data.csv")


# TODO: special models are their own model, i.e. RS6 != A6 (mostly webuycars data)
# GR86 in wbc is currently labelled as 86
# Aggregate Prado models
# fillna on site to be autotrader
# Aggregate porsche cayman
