from datetime import timedelta, datetime

import pandas as pd

from utils import pull_all_data


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
    min = group["price"].min()
    max = group["price"].max()
    ad_id = group["ad_id"].unique()[0]
    time_online = (
        pd.to_datetime(group["date_retrieved"]).max()
        - pd.to_datetime(group["date_retrieved"]).min()
    )
    status = pd.to_datetime(group["date_retrieved"].fillna("").max()) < (
        datetime.now() - timedelta(days=1)
    )
    site = group["site"].unique()[0]
    last_seen = pd.to_datetime(group["date_retrieved"]).max()
    date_scraped = pd.to_datetime(group["date_retrieved"]).min()
    title = group["title"].unique().tolist()[0]
    generation = group["generation"].unique().tolist()[0]
    image_url = group["image_url"].unique().tolist()[-1]  # uh no, won't work
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
            "status": status,
            "site": site,
            "title": title,
            "ad_id": ad_id,
            "image_url": image_url,
        }
    )


def create_image_url_col(df):
    df["image_url"] = df["image_url"].fillna("")
    df.loc[df.site.eq("webuycars"), "image_url"] = (
        "https://photos.webuycars.co.za/photobooth/"
        + df.loc[df.site.eq("webuycars"), "ad_id"]
        + "/Images/"
        + df.loc[df.site.eq("webuycars"), "ad_id"]
        + "0.webp"
    )
    df.loc[
        df.site.eq("autotrader") & ~df.image_url.str.contains("https"), "image_url"
    ] = (
        "https://img.autotrader.co.za/"
        + df.loc[
            df.site.eq("autotrader") & ~df.image_url.str.contains("https"), "image_url"
        ]
        + "/Crop800x600"
    )
    return df


def cleanup_model_names(df):
    df.loc[df.model.eq("1-series"), "model"] = "1 series"
    df.loc[df.model.eq("2-series"), "model"] = "2 series"
    df.loc[df.model.eq("3-series"), "model"] = "3 series"

    df = two_part_search_replace(df, "model", ("yaris", "gr"), "gr yaris")
    df = two_part_search_replace(df, "model", ("corolla", "gr"), "gr corolla")
    df = two_part_search_replace(df, "model", ("supra", "gr"), "gr supra")
    df = two_part_search_replace(df, "model", ("86", "gr"), "gr86")

    df = two_part_search_replace(df, "model", ("911", "gt2"), "911 gt2")
    df = two_part_search_replace(df, "model", ("911", "gt3"), "911 gt3")

    df = two_part_search_replace(df, "model", ("350", "z"), "350z")
    df = two_part_search_replace(df, "model", ("370", "z"), "370z")

    df = two_part_search_replace(df, "model", ("z4", "m coupe"), "z4 m")
    df = two_part_search_replace(df, "model", ("ferrari", "360"), "360")

    df.loc[df.model.eq("prado"), "model"] = "land-cruiser-prado"
    df.loc[df.manufacturer.eq("alfa romeo"), "manufacturer"] = "alfa-romeo"
    df.loc[df.model.eq("c-class/c63/search"), "model"] = "c class"

    df.loc[df.title.str.contains("911"), "model"] = "911"

    return df


def assign_generation(df, generation_mapping):
    for model in generation_mapping.keys():
        for gen in generation_mapping[model]:
            yr_min, yr_max = generation_mapping[model][gen]
            df.loc[
                df.year.between(yr_min, yr_max) & (df.model == model), "generation"
            ] = gen
    return df


def cleanup_price(df):
    df.loc[df.site.eq("webuycars"), "price"] = (
        df.loc[df.site.eq("webuycars"), "price"]
        .str.replace("R ", "")
        .str.replace(" ", "")
    )
    df.loc[df.site.eq("autotrader"), "price"] = (
        df.loc[df.site.eq("autotrader"), "price"]
        .str.split("R")
        .str[1]
        .str.replace(" ", "")
    )
    return df


def assign_website(df):
    df["site"] = "webuycars"
    df.loc[~df.dealer.eq("wbc"), "site"] = "autotrader"
    return df


def cleanup_mileage(df):
    df["mileage"] = pd.to_numeric(
        df["mileage"].str.lower().str.replace("km", "").str.replace(" ", ""),
        errors="coerce",
        downcast="integer",
    )
    return df


def assign_year(df):
    df["year"] = pd.to_numeric(df["title"].str.split(" ").str[0], errors="coerce")
    print(f"Dropping {df['year'].isna().sum()} entries with NaN for year")
    df = df.dropna(subset="year")
    df["year"] = df.year.astype(int)
    return df


def clean_ad_id(df):
    df["ad_id"] = df["ad_id"].astype(str).str.replace(".0", "")
    return df


def two_part_search_replace(df, replace_col, search_val: tuple[str, str], replace):
    df.loc[
        df.title.str.lower().str.contains(search_val[0])
        & df.title.str.lower().str.contains(search_val[1]),
        replace_col,
    ] = replace
    return df


def enforce_numeric(df, cols: list):
    for col in cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def remove_na(df, cols):
    for col in cols:
        print(f"Dropping {df[col].isna().sum()} entries with NaN for {col}")
        df = df.dropna(subset=col)
    return df


def build_display_name(df):
    df["display_name"] = df["manufacturer"].title() + " " + df["model"]
    return df


def standardize_manufacturer_col(df):
    df = two_part_search_replace(df, ("alfa", "romeo"), "Alfa-Romeo")
    df["manufacturer"] = df["manufacturer"].str.title()

    return df


if __name__ == "__main__":
    from pathlib import Path

    df = pull_all_data("listing.db")

    df = two_part_search_replace(df, "manufacturer", ("alfa", "romeo"), "Alfa-Romeo")
    df["manufacturer"] = df["manufacturer"].str.title()

    df.model = df.model.str.lower().astype(str)
    df["submodel"] = ""
    df["generation"] = ""

    df = assign_year(df)
    df = assign_website(df)
    df = cleanup_price(df)
    df = cleanup_mileage(df)
    df = remove_na(df, cols=["price", "mileage", "year"])
    df = enforce_numeric(df, cols=["year", "price", "mileage"])

    df = clean_ad_id(df)
    df = create_image_url_col(df)
    df = assign_generation(df, model_gen_year_mapping)
    df = cleanup_model_names(df)

    df = df.groupby("ad_id").apply(get_the_data).reset_index(drop=True)

    import ipdb

    ipdb.set_trace()
    df["display_name"] = df["manufacturer"] + " " + df["model"]

    data_dir = Path("data")
    df.to_csv(data_dir / "frontend_data.csv")
