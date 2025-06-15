import pandas as pd
import streamlit as st

st.title("Sales and Purchase Data Merger")

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
            "SI",
            "Inv No:",
            "Vouch. Type",
            "Date",
            "Customer Name",
            "Customer  Address",
            "Ref Date",
            "ItemCode_sales",
            "Description",
            "Qty",
            "Unit_sales",
            "Rate_sales",
            "GrossAmt",
            "Net Amount",
            "ItemCode_purchase",
            "Stock",
            "Unit_purchase",
            "Rate_purchase",
            "Stock Value",
            "MRP",
        ]
    ]

    df["net_purchase_amount"] = df.Rate_purchase * 1.18
    df["sale_rate"] = df["Net Amount"] / df.Qty
    df["profit"] = df["sale_rate"] - df["net_purchase_amount"]

    filter_rate = st.sidebar.number_input(
        "Enter the price for AUTO MOTIVE FILTTER", value=35, step=1
    )
    loose_oil_rate = st.sidebar.number_input(
        "Enter the price for LOOSE OIL", value=115, step=1
    )
    if filter_rate:
        df.loc[df["Description"] == "AUTO MOTIVE FILTTER", "net_purchase_amount"] = (
            filter_rate * 1.18
        )
    if loose_oil_rate:
        df.loc[df["Description"] == "LOOSE OIL", "net_purchase_amount"] = (
            loose_oil_rate * 1.18
        )

    # for all items in df with net_purchase_amount less than 10, ask the user to enter the net_purchase_amount
    for index, row in df.iterrows():
        if row["net_purchase_amount"] < 10:
            net_purchase_amount = st.sidebar.text_input(
                "Enter the net purchase amount for " + row["Description"],
                value=row["net_purchase_amount"],
            )
            df.at[index, "net_purchase_amount"] = float(net_purchase_amount)

    df = df[~df["Customer Name"].str.contains("CASH A/C")]
    df["profit"] = df.Qty * (df["sale_rate"] - df.net_purchase_amount)
    df["profit_percentage"] = (
        100 * (df["sale_rate"] - df.net_purchase_amount) / df.net_purchase_amount
    )

    df = df.sort_values(by="profit", ascending=False)

    profit_df = df.groupby("Date")[["profit"]].sum()
    profit_df = profit_df.sort_values(by="profit", ascending=False)

    st.title("Profit Summary")
    st.dataframe(profit_df)

    selected_date = st.sidebar.selectbox("Select a date", profit_df.index)
    date_df = df[df["Date"] == pd.to_datetime(selected_date)]

    st.title("Sales Summary for " + selected_date.strftime("%Y-%m-%d"))
    st.dataframe(date_df)
