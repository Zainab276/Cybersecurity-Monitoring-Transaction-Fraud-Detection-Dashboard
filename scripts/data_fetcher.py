# scripts/data_fetcher.py
import yfinance as yf
import requests
import pandas as pd
import os
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)

def fetch_yfinance(symbols, period_days=365):
    end = datetime.utcnow()
    start = end - timedelta(days=period_days)
    data = {}
    for sym in symbols:
        try:
            df = yf.download(sym, start=start.strftime('%Y-%m-%d'), end=end.strftime('%Y-%m-%d'), progress=False)
            if df is not None and not df.empty:
                df = df[['Close']]
                df.index = df.index.strftime('%Y-%m-%d')
                data[sym] = df
        except Exception:
            data[sym] = None
    return data

def fetch_coingecko(coin_ids, days=365):
    all_data = {}
    for coin in coin_ids:
        try:
            url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart?vs_currency=usd&days={days}&interval=daily"
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            prices = resp.json().get('prices', [])
            df = pd.DataFrame([(datetime.utcfromtimestamp(ts/1000).strftime('%Y-%m-%d'), price) for ts, price in prices], columns=['date','price']).set_index('date')
            all_data[coin] = df
        except Exception:
            all_data[coin] = None
    return all_data

def save_data(dct):
    for name, df in dct.items():
        if df is None: continue
        path = os.path.join(DATA_DIR, f"{name}.csv")
        df.to_csv(path)
