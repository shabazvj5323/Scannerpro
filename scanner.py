import yfinance as yf
import os
from datetime import datetime
import pytz
from concurrent.futures import ThreadPoolExecutor

base_path = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(base_path, 'tickers.txt'), 'r') as f:
    tickers = [line.strip() for line in f.readlines() if line.strip()]

def check_stock(ticker):
    try:
        # 1. Live 5m Data (Strategy 1)
        df_5m = yf.download(ticker, period='5d', interval='5m', progress=False)
        # 2. Daily Data (Strategy 2 & 3)
        df_1d = yf.download(ticker, period='3mo', interval='1d', progress=False)
        
        if len(df_5m) < 100 or len(df_1d) < 50: return None
        
        # Calculations
        df_5m['EMA20'] = df_5m['Close'].ewm(span=20).mean()
        df_5m['EMA50'] = df_5m['Close'].ewm(span=50).mean()
        df_5m['Vol_SMA'] = df_5m['Volume'].rolling(window=20).mean()
        
        df_1d['EMA20'] = df_1d['Close'].ewm(span=20).mean()
        df_1d['EMA30'] = df_1d['Close'].ewm(span=30).mean()
        df_1d['EMA50'] = df_1d['Close'].ewm(span=50).mean()
        df_1d['Vol_SMA'] = df_1d['Volume'].rolling(window=10).mean()
        
        last_5m = df_5m.iloc[-1]
        prev_1d = df_1d.iloc[-2] # Kal ka closing data
        
        # Strategies
        s1 = (last_5m['EMA20'] > last_5m['EMA50']) and (last_5m['Volume'] > last_5m['Vol_SMA'] * 1.5)
        s2 = (prev_1d['EMA20'] > prev_1d['EMA30'] > prev_1d['EMA50'])
        s3 = (prev_1d['EMA20'] > prev_1d['EMA30'] > prev_1d['EMA50']) and (prev_1d['Volume'] > prev_1d['Vol_SMA'] * 1.10)
        
        return {'ticker': ticker, 's1': s1, 's2': s2, 's3': s3}
    except:
        return None

# ... (baaki ka code waisa hi rahega)
