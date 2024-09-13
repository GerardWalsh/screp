import pandas as pd
from utils import pull_all_data
from datetime import timedelta, datetime
import traceback


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
    ad_id = group["ad_id"].unique()[0]
    time_online = (
        pd.to_datetime(group["date_retrieved"]).max()
        - pd.to_datetime(group["date_retrieved"]).min()
    )
    sold = pd.to_datetime(group["date_retrieved"].fillna("").max()) < (
        datetime.now() - timedelta(days=1)
    )
    site = group["site"].unique()[0]
    last_seen = pd.to_datetime(group["date_retrieved"]).max()
    date_scraped = pd.to_datetime(group["date_retrieved"]).min()
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
            "ad_id": ad_id,
            "image_url": image_url,
        }
    )


df = pull_all_data("listing.db")
df.model = df.model.fillna("").str.lower()
df["submodel"] = ""
df["generation"] = ""
df["year"] = pd.to_numeric(df["title"].str.split(" ").str[0])


df["site"] = "webuycars"
df.loc[~df.dealer.eq("wbc"), "site"] = "autotrader"



df.loc[
    ~df[["model", "title"]]
    .fillna("")
    .apply(lambda x: x.model in x.title.lower(), axis=1)
].model.unique()

df.loc[df.manufacturer.eq("alfa romeo"), "manufacturer"] = "alfa-romeo"
df.to_csv("data.csv")

df = pd.read_csv("data.csv")
for col in ["year", "price", "mileage"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(999).astype(int)

df = df.groupby("ad_id").apply(get_the_data).reset_index(drop=True)
df.to_csv("frontend_data.csv")

# TODO: special models are their own model, i.e. RS6 != A6 (mostly webuycars data)
# GR86 in wbc is currently labelled as 86
# Aggregate Prado models
# fillna on site to be autotrader
# Aggregate porsche cayman
# except Exception as exception:
#     traceback.print_exception(exception)
#     import ipdb

#     ipdb.set_trace()

def create_image_url_col(df):
    df.loc[df.site.eq("webuycars"), "image_url"] = (
        "https://photos.webuycars.co.za/photobooth/"
        + df.loc[df.site.eq("webuycars")].ad_id
        + "/Images/"
        + df.loc[df.site.eq("webuycars")].ad_id
        + "0.webp"
    )

    df.loc[df.site.eq("autotrader"), "image_url"] = (
        "https://img.autotrader.co.za/"
        + df.loc[df.site.eq("autotrader"), "ad_id"]
        + "/Crop800x600"
    )
    return df

def cleanup_model_names(df, model_name_mapping):
    df.loc[df.model.eq("1-series"), "model"] = "1 series"
    df.loc[df.model.eq("2-series"), "model"] = "2 series"
    df.loc[df.model.eq("3-series"), "model"] = "3 series"

    df.loc[
        df.title.str.lower().str.contains("yaris")
        & df.title.str.lower().str.contains("gr"),
        "model",
    ] = "gr yaris"

    df.loc[
        df.title.str.lower().str.contains("corolla")
        & df.title.str.lower().str.contains("gr"),
        "model",
    ] = "gr corolla"

    df.loc[
        df.title.str.lower().str.contains("911")
        & df.title.str.lower().str.contains("gt2"),
        "model",
    ] = "911 gt2"
    df.loc[
        df.title.str.lower().str.contains("911")
        & df.title.str.lower().str.contains("gt3"),
        "model",
    ] = "911 gt3"

    df.loc[df.model.eq("prado"), "model"] = "land-cruiser-prado"
    df.loc[df.manufacturer.eq("alfa romeo"), "manufacturer"] = "alfa-romeo"
    df.loc[df.model.eq("c-class/c63/search"), "model"] = "c class"
    return df

def assign_generation(df, generation_mapping):  
    for model in generation_mapping.keys():
        for gen in generation_mapping[model]:
            yr_min, yr_max = generation_mapping[model][gen]
            df.loc[
                df.year.between(yr_min, yr_max) & (df.model == model), "generation"
            ] = gen
    return df