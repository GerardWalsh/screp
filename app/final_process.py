import pandas as pd

fdf = pd.read_csv("frontend_data.csv", index_col=0)
fdf.site = fdf.site.fillna("autotrader")

fdf.loc[fdf.site.eq("webuycars"), "link"] = (
    "https://www.webuycars.co.za/buy-a-car/"
    + fdf.loc[fdf.site.eq("webuycars"), "manufacturer"].str.title()
    + "/"
    + fdf.loc[fdf.site.eq("webuycars"), "model"].str.title()
    + "/"
    + fdf.loc[fdf.site.eq("webuycars"), "link"]
).values.tolist()

fdf.link = fdf.link.str.replace("Bmw", "BMW")
fdf.loc[fdf.sold, "link"] = None

fdf[
    [
        "image_url",
        "link",
        "title",
        "manufacturer",
        "model",
        "generation",
        "year",
        "min_price",
        "max_price",
        "mileage",
        "time_online",
        "last_seen",
        "date_listed",
        "sold",
        "site",
    ]
].to_csv("frontend_data.csv")
