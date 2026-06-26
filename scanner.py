import yfinance as yf
import os
from datetime import datetime
import pytz
from concurrent.futures import ThreadPoolExecutor

# Path setup
base_path = os.path.dirname(os.path.abspath(__file__))
tickers_path = os.path.join(base_path, 'tickers.txt')

with open(tickers_path, 'r') as f:
    tickers = [line.strip() for line in f.readlines() if line.strip()]

def check_stock(ticker):
    try:
        # Data fetch
        df_5m = yf.download(ticker, period='5d', interval='5m', progress=False)
        df_1d = yf.download(ticker, period='3mo', interval='1d', progress=False)
        
        if len(df_5m) < 50 or len(df_1d) < 50: return None
        
        # 5m Indicators
        df_5m['EMA20'] = df_5m['Close'].ewm(span=20).mean()
        df_5m['EMA50'] = df_5m['Close'].ewm(span=50).mean()
        df_5m['Vol_SMA'] = df_5m['Volume'].rolling(window=20).mean()
        
        # 1d Indicators
        df_1d['EMA20'] = df_1d['Close'].ewm(span=20).mean()
        df_1d['EMA30'] = df_1d['Close'].ewm(span=30).mean()
        df_1d['EMA50'] = df_1d['Close'].ewm(span=50).mean()
        df_1d['Vol_SMA'] = df_1d['Volume'].rolling(window=10).mean()
        
        last_5m = df_5m.iloc[-1]
        prev_1d = df_1d.iloc[-2]
        
        # --- TEST MODE LOGIC ---
        s1 = True  # Sabhi stocks dikhenge
        # --- ORIGINAL STRATEGY ---
        s2 = (prev_1d['EMA20'] > prev_1d['EMA30'] > prev_1d['EMA50'])
        s3 = (prev_1d['EMA20'] > prev_1d['EMA30'] > prev_1d['EMA50']) and (prev_1d['Volume'] > prev_1d['Vol_SMA'] * 1.10)
        
        return {'ticker': ticker, 's1': s1, 's2': s2, 's3': s3}
    except:
        return None

# Process
with ThreadPoolExecutor(max_workers=10) as executor:
    results = [res for res in executor.map(check_stock, tickers) if res is not None]

def get_html_list(condition_key):
    filtered = [r['ticker'] for r in results if r[condition_key]]
    if not filtered: return "<li>No signals</li>"
    items = ""
    for s in filtered:
        symbol = s.replace(".NS", "")
        items += f'<li><strong>{symbol}</strong>: <a href="https://in.tradingview.com/chart/?symbol=NSE:{symbol}" target="_blank">TV</a> | <a href="https://kite.zerodha.com/chart/ext/bid/NSE/{symbol}" target="_blank">Zerodha</a></li>'
    return items

# Final HTML Generator
html_content = f"""
<html>
<head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body>
<h3>🚀 S1: TEST MODE (Active)</h3><ul>{get_html_list('s1')}</ul>
<hr>
<h3>📅 S2: Prev Day Trend (20>30>50)</h3><ul>{get_html_list('s2')}</ul>
<hr>
<h3>💎 S3: Strict Prev (20>30>50 + 10% Vol)</h3><ul>{get_html_list('s3')}</ul>
<p>Last Update: {datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%d-%m %H:%M:%S")}</p>
</body>
</html>
"""

# Write to file
with open(os.path.join(base_path, "index.html"), "w") as f:
    f.write(html_content)
    print("File written successfully")
    
