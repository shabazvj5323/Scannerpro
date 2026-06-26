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
        # Period 5d lene se ye pichla valid data utha lega
        df = yf.download(ticker, period='5d', interval='1d', progress=False)
        if len(df) < 5: return None
        
        df['EMA20'] = df['Close'].ewm(span=20).mean()
        df['EMA30'] = df['Close'].ewm(span=30).mean()
        df['EMA50'] = df['Close'].ewm(span=50).mean()
        df['Vol_SMA'] = df['Volume'].rolling(window=10).mean()
        
        # Last valid data uthana
        last = df.dropna().iloc[-1]
        
        s1 = (last['EMA20'] > last['EMA30'] > last['EMA50']) and (last['Volume'] > last['Vol_SMA'] * 1.10)
        s2 = (last['EMA20'] > last['EMA50']) and (last['Volume'] > last['Vol_SMA'] * 1.02)
        s3 = s1 
        
        return {'ticker': ticker, 's1': s1, 's2': s2, 's3': s3}
    except:
        return None

# Parallel processing
results = [res for res in ThreadPoolExecutor(max_workers=20).map(check_stock, tickers) if res is not None]

s1_list = [r['ticker'] for r in results if r['s1']]
s2_list = [r['ticker'] for r in results if r['s2']]
s3_list = [r['ticker'] for r in results if r['s3']]

def get_html_list(stock_list):
    if not stock_list: return "<p>No signals</p>"
    items = ""
    for s in stock_list:
        symbol = s.replace(".NS", "")
        items += f'''
        <div class="stock-item">
            <strong>{s}</strong><br>
            <div class="links">
                <a href="https://in.tradingview.com/chart/?symbol=NSE:{symbol}" target="_blank">TradingView</a> |
                <a href="https://kite.zerodha.com/chart/ext/bid/NSE/{symbol}" target="_blank">Zerodha</a> |
                <a href="https://groww.in/stocks/{symbol.lower()}-ltd" target="_blank">Groww</a>
            </div>
        </div>'''
    return items

html_content = f"""
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: sans-serif; background: #f4f7f6; padding: 15px; }}
        .card {{ background: white; padding: 15px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }}
        .stock-item {{ padding: 12px; border-bottom: 1px solid #eee; }}
        .links {{ font-size: 13px; margin-top: 6px; }}
        a {{ text-decoration: none; color: #1976d2; font-weight: bold; }}
        h2 {{ color: #d32f2f; font-size: 18px; }}
    </style>
</head>
<body>
    <div class="card">
        <h2>🚀 Strategy 1 (Strict)</h2> {get_html_list(s1_list)}
        <hr>
        <h2>⚡ Strategy 2 (Loose)</h2> {get_html_list(s2_list)}
        <hr>
        <h2>📅 Strategy 3 (Latest Available)</h2> {get_html_list(s3_list)}
        <p style="font-size: 10px; color: #777;">Last Scan: {datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%d-%m %H:%M:%S IST")}</p>
    </div>
</body>
</html>
"""
with open("index.html", "w") as f: f.write(html_content)
    
