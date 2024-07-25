import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

from datetime import timedelta, date, time
from datetime import datetime

st.set_page_config(layout="wide")


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
            "mileage": group["mileage"].fillna(999).astype(int).unique().tolist()[0],
            "sold": sold,
            "site": site,
            "title": title,
            "link": link,
            "image_url": image_url,
        }
    )


# Load the CSV file
@st.cache
def load_data():
    df = pd.read_csv("data.csv")
    for col in ["year", "price", "mileage"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(999).astype(int)

    df = df.groupby("link").apply(get_the_data).reset_index(drop=True)
    df.to_csv("frontend_data.csv")
    return df


def main():
    st.title("Cars & stuff")
    # df = load_data()
    page = st.selectbox(
        "App functionality",
        [
            "Please choose an option",
            "market overview",
            "price estimation",
            "sales report",
        ],
    )

    df = pd.read_csv("frontend_data.csv", index_col=0)
    df.time_online = pd.to_timedelta(df.time_online).round("1 min")
    df.last_seen = pd.to_datetime(df.last_seen).round("60 min")
    filter_map = {
        "model": [
            " ".join(x).title()
            for x in sorted(df[["manufacturer", "model"]].value_counts().index.tolist())
        ],
        "manufacturer": [
            "alfa-romeo",
            "audi",
            "bmw",
            "ferrari",
            "honda",
            "jaguar",
            "mclaren",
            "mercedes-amg",
            "mercedes-benz",
            "nissan",
            "porsche",
            "renault",
            "suzuki",
            "toyota",
        ],
    }
    df = df.dropna(subset="model")
    if page == "market overview":
        column = st.selectbox(
            "Select column to filter by", ["model", "manufacturer", "generation"], index=0
        )
        unique_values = filter_map[column]
        filter_value = st.selectbox(
            f"Select the {column} to filter by", unique_values, index=8
        )

        # Filter dataframe
        if column == "model":
            filter_value = " ".join(filter_value.split(" ")[1:]).lower()
        elif column == "manufacturer":
            filter_value = filter_value

        filtered_df = df[df[column] == filter_value]

        if filtered_df.generation.any():
            gen = filtered_df.generation.unique().tolist()
            gen_filter = st.multiselect("Select the generation to filter by", gen)
            if gen_filter != []:
                filtered_df = filtered_df[filtered_df.generation.isin(gen_filter)]

        tag_filter = st.text_input(
            "Search by keyword (try: 'sport', 'touring', 'automatic')",
            key="placeholder",
        )
        if tag_filter:
            filtered_df = filtered_df[
                filtered_df.title.fillna("").str.lower().str.contains(tag_filter.lower())
            ]
        appointment = st.slider(
            "Model year range:",
            value=(filtered_df.year.min(), filtered_df.year.max()),
            min_value=1980,
            max_value=2024,
        )
        filtered_df = filtered_df[
            filtered_df.year.between(appointment[0], appointment[1])
        ]
        # Display filtered dataframe
        st.write(f"Filtered Dataframe based on {column} = {filter_value}")
        st.dataframe(
            filtered_df,
            use_container_width=True,
            column_config={
                "image_url": st.column_config.ImageColumn(label="image_url"),
                "link": st.column_config.LinkColumn("link"),
            },
            hide_index=True,
        )

        st.write("Sold vs listed prices, against year")
        if "max_price" in df.columns and "year" in df.columns:
            avg_price_per_year = (
                filtered_df.groupby(["year", "sold"])["max_price"].mean().reset_index()
            )
            color_discrete_map = {
                1: "rgb(255,0,0)",
                2: "rgb(0,255,0)",
            }
            # print(filtered_df)
            fig = px.scatter(
                filtered_df,
                x="year",
                y="max_price",
                color="sold",
                hover_data=["max_price"],
                color_discrete_map={False: "#316295", True: "#B82E2E"},
            )
            event = st.plotly_chart(fig, key="iris", on_select="rerun")
            # event
            plt.title("Average Price Against Year")
            plt.xlabel("Year")
            plt.ylabel("Average Price")
            plt.xticks(rotation=45)
    elif page == "price estimation":
        st.write("Coming soon!")
        # model = st.selectbox("select your model", filter_map["model"])
        # model = " ".join(model.split(" ")[1:]).lower()
        # mileage = st.text_input("Enter your mileage")
        # year = st.text_input("Enter the year")
        # generate_report = st.button("generate price!")
        # if generate_report:
        #     mileage = int(mileage)
        #     data = df[
        #         df.model.eq(model) & df.mileage.between(mileage - 1000, mileage + 1000)
        #     ]
        #     st.write("30 thousands dollars Jordan! R", data.max_price.mean())
    elif page == "sales report":
        st.write("Coming soon!")
        # model = st.selectbox("select your model", filter_map["model"])
        # model = " ".join(model.split(" ")[1:]).lower()
        # # mileage = st.text_input("Enter your mileage")
        # year = st.text_input("Enter the year")
        # generate_report = st.button("generate price!")
        # if generate_report:
        #     #     mileage = int(mileage)
        #     #     data = df[
        #     #         df.model.eq(model) & df.mileage.between(mileage - 1000, mileage + 1000)
        #     #     ]
        #     st.write("30 thousands dollars Jordan!")


if __name__ == "__main__":
    main()

# TODO
# add keyword search to app, with steps to confirm model
