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
    print("Error: tickers.txt file nahi mili!")
    tickers = []

def check_stock(ticker):
    try:
        # Data fetch - 1.5 mahine ka data kaafi hai tez scan ke liye
        df = yf.download(ticker, period='1.5mo', interval='1d', progress=False)
        if len(df) < 40: return None
        
        # EMA Calculations
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

# Multithreading (25 workers taaki 500 stocks jaldi ho jayein)
signals = []
with ThreadPoolExecutor(max_workers=25) as executor:
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
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f4f7f6; padding: 20px; }}
        .card {{ background: white; padding: 20px; border-radius: 15px; box-shadow: 0 10px 20px rgba(0,0,0,0.05); }}
        h2 {{ color: #2c3e50; border-bottom: 2px solid #e74c3c; padding-bottom: 10px; }}
        ul {{ list-style: none; padding: 0; }}
        li {{ padding: 12px; border-bottom: 1px solid #eee; color: #27ae60; font-weight: 700; font-size: 16px; }}
        .time {{ font-size: 12px; color: #7f8c8d; margin-top: 20px; text-align: center; }}
    </style>
</head>
<body>
    <div class="card">
        <h2>🚀 Nifty 500 Scanner</h2>
        {'<ul>' + ''.join([f'<li>✅ {s}</li>' for s in signals]) + '</ul>' if signals else '<p>• No signals right now.</p>'}
        <div class="time">Last Scan: {update_time}</div>
    </div>
</body>
</html>
"""

with open("index.html", "w") as f:
    f.write(html_content)
print(f"Scan complete. {len(signals)} signals found.")
