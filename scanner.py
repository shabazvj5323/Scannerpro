import yfinance as yf
import os
from datetime import datetime
import pytz
from concurrent.futures import ThreadPoolExecutor

# Path setup
base_path = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(base_path, 'tickers.txt'), 'r') as f:
    tickers = [line.strip() for line in f.readlines() if line.strip()]

def check_stock(ticker):
    try:
        # EMA calculation ke liye 3 mahine ka data
        df = yf.download(ticker, period='3mo', interval='1d', progress=False)
        if len(df) < 50: return None
        
        df['EMA20'] = df['Close'].ewm(span=20).mean()
        df['EMA30'] = df['Close'].ewm(span=30).mean()
        df['EMA50'] = df['Close'].ewm(span=50).mean()
        df['Vol_SMA'] = df['Volume'].rolling(window=10).mean()
        
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Strategies
        s1 = (last['EMA20'] > last['EMA30'] > last['EMA50']) and (last['Volume'] > last['Vol_SMA'] * 1.05)
        s2 = (last['EMA20'] > last['EMA50']) and (last['Volume'] > last['Vol_SMA'] * 1.05)
        s3 = (prev['EMA20'] > prev['EMA30'] > prev['EMA50']) and (prev['Volume'] > prev['Vol_SMA'] * 1.05)
        
        return {'ticker': ticker, 's1': s1, 's2': s2, 's3': s3}
    except:
        return None

# Parallel processing
with ThreadPoolExecutor(max_workers=20) as executor:
    results = [res for res in executor.map(check_stock, tickers) if res is not None]

def get_html_list(condition_key):
    filtered = [r['ticker'] for r in results if r[condition_key]]
    if not filtered: return "<li>No signals</li>"
    items = ""
    for s in filtered:
        symbol = s.replace(".NS", "")
        items += f'''
        <li style="margin-bottom:12px; border-bottom:1px solid #eee; padding-bottom:5px;">
            <strong>{symbol}</strong><br>
            <a href="https://in.tradingview.com/chart/?symbol=NSE:{symbol}" target="_blank">TradingView</a> | 
            <a href="https://kite.zerodha.com/chart/ext/bid/NSE/{symbol}" target="_blank">Zerodha</a> | 
            <a href="https://groww.in/stocks/{symbol.lower()}-ltd" target="_blank">Groww</a>
        </li>'''
    return items

# Generate HTML
html_content = f"""
<html>
<head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="font-family: sans-serif; padding: 10px;">
<h3>🚀 S1: Strict Live</h3><ul>{get_html_list('s1')}</ul>
<hr>
<h3>⚡ S2: Loose Live</h3><ul>{get_html_list('s2')}</ul>
<hr>
<h3>📅 S3: Strict Previous Close</h3><ul>{get_html_list('s3')}</ul>
<p style="font-size:11px; color:gray;">Last Scan: {datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%d-%m %H:%M:%S")}</p>
</body>
</html>
"""

with open("index.html", "w") as f: f.write(html_content)
    
