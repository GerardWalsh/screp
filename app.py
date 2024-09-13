import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

st.set_page_config(layout="wide")


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
        filtered_df = filtered_df.rename(columns={"sold": "status"})
        filtered_df.status = filtered_df.status.map({False: "available", True: "sold"})
        st.write(f"Filtered Dataframe based on {column} = {filter_value}")
        st.dataframe(
            filtered_df[
                [
                    "image_url",
                    "title",
                    # "generation",
                    "min_price",
                    "max_price",
                    "year",
                    "mileage",
                    "status",
                    "time_online",
                    # "link",
                    "site",
                    "date_listed",
                    "last_seen",
                ]
            ].rename(
                columns={
                    "min_price": "min_listed_price",
                    "max_price": "max_listed_price",
                    "image_url": "image_url (click me!)",
                }
            ),
            use_container_width=True,
            column_config={
                "image_url (click me!)": st.column_config.ImageColumn(
                    label="image_url (click me!)"
                ),
                "link": st.column_config.LinkColumn("link"),
            },
            hide_index=True,
        )

        st.write("Sold vs listed prices, against year")
        if "max_price" in df.columns and "year" in df.columns:
            avg_price_per_year = (
                filtered_df.groupby(["year", "status"])["max_price"].mean().reset_index()
            )
            color_discrete_map = {
                1: "rgb(255,0,0)",
                2: "rgb(0,255,0)",
            }
            fig = px.scatter(
                filtered_df.assign(),
                x="date_listed",
                y="max_price",
                color="status",
                hover_data={
                    "mileage": True,
                    "status": False,
                    "last_seen": True,
                    "date_listed": False,
                },
                color_discrete_map={"available": "#316295", "sold": "#B82E2E"},
            )
            event = st.plotly_chart(fig, key="iris", on_select="rerun")
            # event
            plt.title("Average Price Against Year")
            plt.xlabel("Year")
            plt.ylabel("Average Price")
            plt.xticks(rotation=45)
    elif page == "price estimation":
        st.write("Coming soon!")
        model = st.selectbox("select your model", filter_map["model"])
        similar_mileage = st.slider(
            "Mileage offset:",
            value=(-10000, 10000),
            min_value=-20000,
            max_value=20000,
        )
        model = " ".join(model.split(" ")[1:]).lower()
        mileage = st.text_input("Enter your mileage")
        year = st.text_input("Enter the year")
        generate_report = st.button("generate price!")
        if generate_report:
            mileage = int(mileage)
            data = df[
                df.model.eq(model)
                & df.year.eq(int(year))
                & df.mileage.between(
                    mileage + similar_mileage[0], mileage + similar_mileage[1]
                )
            ][
                [
                    "title",
                    "generation",
                    "max_price",
                    "mileage",
                    "sold",
                    "time_online",
                    "link",
                ]
            ]
            st.write("Similar ads for year & mileage range")
            st.dataframe(
                data,
                column_config={
                    "link": st.column_config.LinkColumn("link"),
                },
            )
            st.write(
                f"Mean price for year model and mileage range: R{ data.max_price.mean()}",
            )
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
