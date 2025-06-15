import pandas as pd
import streamlit as st

st.title("Profit Calculator")

df1 = st.sidebar.file_uploader("Upload Sales Register", type=["xlsx"])
df2 = st.sidebar.file_uploader("Upload Purchase", type=["xlsx"])

if df1 and df2:
    df1 = pd.read_excel(df1)
    df2 = pd.read_excel(df2)

    df1 = df1.iloc[4:]
    df1.columns = df1.iloc[0]
    df1 = df1.iloc[1:]

    df2 = df2.iloc[4:]
    df2.columns = df2.iloc[0]
    df2 = df2.iloc[1:]

    df = pd.merge(
        df1, df2, on="Description", how="inner", suffixes=("_sales", "_purchase")
    )

    df = df[
        [
            "Inv No:",
            "Date",
            "Customer Name",
            "Customer  Address",
            "Description",
            "Qty",
            "Rate_sales",
            "Net Amount",
            "Stock",
            "Rate_purchase",
            "Stock Value",
            "MRP",
        ]
    ]

    df["net_purchase_amount"] = df.Rate_purchase * 1.18
    df["sale_rate"] = df["Net Amount"] / df.Qty
    df["profit"] = df["sale_rate"] - df["net_purchase_amount"]

    # filter_rate = st.sidebar.number_input(
    #     "Enter the price for AUTO MOTIVE FILTTER", value=35, step=1
    # )
    # loose_oil_rate = st.sidebar.number_input(
    #     "Enter the price for SAVOLOOSE OIL", value=115, step=1
    # )
    # if filter_rate:
    #     df.loc[df["Description"] == "AUTO MOTIVE FILTTER", "net_purchase_amount"] = (
    #         filter_rate * 1.18
    #     )
    # if loose_oil_rate:
    #     df.loc[df["Description"] == "SAVO LOOSE OIL", "net_purchase_amount"] = (
    #         loose_oil_rate * 1.18
    #     )

    # for unique description in df with net_purchase_amount less than 10, ask the user to enter the net_purchase_amount
    for description in df["Description"].unique():
        if df[df["Description"] == description]["net_purchase_amount"].min() < 10:
            # st.write(description)
            net_purchase_amount = st.sidebar.text_input(
                "purchase amount for " + description,
                value=df[df["Description"] == description]["net_purchase_amount"].min(),
                key=description,
            )
            df.loc[df["Description"] == description, "net_purchase_amount"] = float(
                net_purchase_amount
            )

    df = df[~df["Customer Name"].str.contains("CASH A/C")]
    df["profit"] = df.Qty * (df["sale_rate"] - df.net_purchase_amount)

    for description in df["Description"].unique():
        if df[df["Description"] == description]["profit"].min() < 0:
            # st.write(description)
            net_purchase_amount = st.sidebar.text_input(
                "purchase amount for " + description,
                value=df[df["Description"] == description]["net_purchase_amount"].min(),
                key=description,
            )
            df.loc[df["Description"] == description, "net_purchase_amount"] = float(
                net_purchase_amount
            )
    df["profit"] = df.Qty * (df["sale_rate"] - df.net_purchase_amount)

    if df.net_purchase_amount.min() > 10:
        df["profit_percentage"] = (
            100 * (df["sale_rate"] - df.net_purchase_amount) / df.net_purchase_amount
        )

    # df = df.sort_values(by="profit", ascending=False)

    profit_df = (df.groupby("Date")[["profit"]].sum()).reset_index()
    # profit_df = profit_df.sort_values(by="profit", ascending=False)
    profit_df["Date"] = profit_df["Date"].dt.strftime("%d-%m-%Y")
    st.title("Profit Summary")
    total_profit = profit_df["profit"].sum()
    st.write("Total Profit: " + str(total_profit))
    st.dataframe(profit_df)

    selected_date = st.sidebar.selectbox("Select a date", profit_df.Date)
    date_df = df[df["Date"] == pd.to_datetime(selected_date)]

    st.title("Sales Summary for " + selected_date)
    st.dataframe(date_df)
