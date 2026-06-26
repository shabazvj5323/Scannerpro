import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz
from concurrent.futures import ThreadPoolExecutor

# Tickers load karna
with open('tickers.txt', 'r') as f:
    tickers = [line.strip() for line in f.readlines() if line.strip()]

def check_stock(ticker):
    try:
        df = yf.download(ticker, period='3mo', interval='1d', progress=False)
        if len(df) < 50: return None
        
        df['EMA20'] = df['Close'].ewm(span=20).mean()
        df['EMA30'] = df['Close'].ewm(span=30).mean()
        df['EMA50'] = df['Close'].ewm(span=50).mean()
        df['Vol_SMA'] = df['Volume'].rolling(window=10).mean()
        last = df.iloc[-1]
        
        # Strategy 1: Strict (Trend + 10% Volume spike)
        s1 = (last['EMA20'] > last['EMA30'] > last['EMA50']) and (last['Volume'] > last['Vol_SMA'] * 1.10)
        
        # Strategy 2: Loose (Trend + 2% Volume spike)
        s2 = (last['EMA20'] > last['EMA50']) and (last['Volume'] > last['Vol_SMA'] * 1.02)
        
        return {'ticker': ticker, 's1': s1, 's2': s2}
    except:
        return None

results = []
with ThreadPoolExecutor(max_workers=20) as executor:
    results = [res for res in executor.map(check_stock, tickers) if res is not None]

s1_list = [r['ticker'] for r in results if r['s1']]
s2_list = [r['ticker'] for r in results if r['s2']]

# UI Generation
ist = pytz.timezone('Asia/Kolkata')
update_time = datetime.now(ist).strftime("%d-%m-%Y %H:%M:%S IST")

html_content = f"""
<html>
<body>
    <h2>🚀 Strategy 1 (Strict):</h2>
    {'<ul>' + ''.join([f'<li>{s}</li>' for s in s1_list]) + '</ul>' if s1_list else '<p>No signals</p>'}
    
    <hr>
    
    <h2>⚡ Strategy 2 (Loose):</h2>
    {'<ul>' + ''.join([f'<li>{s}</li>' for s in s2_list]) + '</ul>' if s2_list else '<p>No signals</p>'}
    
    <p>Last Scan: {update_time}</p>
</body>
</html>
"""
with open("index.html", "w") as f: f.write(html_content)
    
