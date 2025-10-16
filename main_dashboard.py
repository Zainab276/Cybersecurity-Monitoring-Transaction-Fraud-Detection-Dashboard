import streamlit as st
import pandas as pd
from scripts.data_fetcher import fetch_yfinance, fetch_coingecko, save_data
import plotly.express as px

st.set_page_config(page_title="Market Dashboard", layout="wide")
st.title("📊 Financial Market Dashboard — Sparking Asia")

psx = st.text_input("PSX tickers (comma-separated)", "OGDC.PK,PPL.PK,HBL.PK")
us = st.text_input("US tickers (comma-separated)", "AAPL,MSFT,TSLA")
cryptos = st.text_input("Crypto ids (CoinGecko)", "bitcoin,ethereum,solana")

if st.button("Fetch / Refresh Live Data"):
    st.info("Fetching data...")
    yf_symbols = psx.split(',') + us.split(',')
    yf_data = fetch_yfinance(yf_symbols)
    cg_data = fetch_coingecko(cryptos.split(','))
    save_data(yf_data)
    save_data(cg_data)
    st.success("Data fetched successfully!")

    # Display US/PSX Stocks
    st.subheader("US/PSX Stocks (Last Close)")
    for sym, df in yf_data.items():
        if df is not None:
            st.write(f"**{sym}**")
            st.dataframe(df.tail(5))

    # Display Crypto
    st.subheader("Crypto Prices (last 5 days)")
    for coin, df in cg_data.items():
        if df is not None:
            st.write(f"**{coin}**")
            st.dataframe(df.tail(5))

    # Example interactive chart for AAPL
    if 'AAPL' in yf_data and yf_data['AAPL'] is not None:
        fig = px.line(yf_data['AAPL'], y='Close', title="AAPL Price Trend")
        st.plotly_chart(fig)
