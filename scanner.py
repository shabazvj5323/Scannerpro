import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz
from concurrent.futures import ThreadPoolExecutor

# Tickers file se load karna
try:
    with open('tickers.txt', 'r') as f:
        tickers = [line.strip() for line in f.readlines() if line.strip()]
except:
    tickers = []

def check_stock(ticker):
    try:
        # Fixed: '3mo' is a valid period
        df = yf.download(ticker, period='3mo', interval='1d', progress=False)
        if len(df) < 50: return None
        
        df['EMA20'] = df['Close'].ewm(span=20).mean()
        df['EMA30'] = df['Close'].ewm(span=30).mean()
        df['EMA50'] = df['Close'].ewm(span=50).mean()
        df['Vol_SMA'] = df['Volume'].rolling(window=10).mean()
        
        last = df.iloc[-1]
        
        # Strategy: EMA alignment + 10% Volume growth
        if (last['EMA20'] > last['EMA30'] > last['EMA50']) and (last['Volume'] > last['Vol_SMA'] * 1.10):
            return ticker
    except:
        return None

# Multithreading (20 workers balance ke liye)
signals = []
with ThreadPoolExecutor(max_workers=20) as executor:
    results = executor.map(check_stock, tickers)
    signals = [r for r in results if r is not None]

# UI Generation
ist = pytz.timezone('Asia/Kolkata')
update_time = datetime.now(ist).strftime("%d-%m-%Y %H:%M:%S IST")

html_content = f"""
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: sans-serif; background: #f4f7f6; padding: 20px; }}
        .card {{ background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }}
        h2 {{ color: #d32f2f; margin-top: 0; }}
        li {{ padding: 10px; border-bottom: 1px solid #eee; font-weight: bold; color: #2e7d32; }}
        .time {{ font-size: 11px; color: #7f8c8d; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="card">
        <h2>🔥 Nifty 500 Scanner</h2>
        {'<ul>' + ''.join([f'<li>✅ {s}</li>' for s in signals]) + '</ul>' if signals else '<p>• No signals found.</p>'}
        <div class="time">Last Scan: {update_time}</div>
    </div>
</body>
</html>
"""

with open("index.html", "w") as f:
    f.write(html_content)
    
