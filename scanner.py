import yfinance as yf
import os
from datetime import datetime
import pytz
from concurrent.futures import ThreadPoolExecutor

base_path = os.path.dirname(os.path.abspath(__file__))
tickers_path = os.path.join(base_path, 'tickers.txt')

with open(tickers_path, 'r') as f:
    tickers = [line.strip() for line in f.readlines() if line.strip()]

def check_stock(ticker):
    try:
        df_5m = yf.download(ticker, period='5d', interval='5m', progress=False)
        df_1d = yf.download(ticker, period='3mo', interval='1d', progress=False)
        
        if len(df_5m) < 50 or len(df_1d) < 50: return None
        
        last_5m = df_5m.iloc[-1]
        prev_1d = df_1d.iloc[-2]
        
        # TEST MODE: Sab kuch TRUE kar diya hai taki list dikhe
        return {'ticker': ticker, 's1': True, 's2': True, 's3': True}
    except:
        return None

with ThreadPoolExecutor(max_workers=10) as executor:
    results = [res for res in executor.map(check_stock, tickers) if res is not None]

def get_html_list(condition_key):
    filtered = [r['ticker'] for r in results if r[condition_key]]
    if not filtered: return "<li>No signals</li>"
    items = ""
    for s in filtered:
        symbol = s.replace(".NS", "")
        items += f'<li><strong>{symbol}</strong>: <a href="https://in.tradingview.com/chart/?symbol=NSE:{symbol}" target="_blank">TV</a></li>'
    return items

html_content = f"""
<html>
<head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body>
<h3>🚀 TEST MODE: ALL STOCKS</h3><ul>{get_html_list('s1')}</ul>
<p>Last Update: {datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%d-%m %H:%M:%S")}</p>
</body>
</html>
"""

with open(os.path.join(base_path, "index.html"), "w") as f:
    f.write(html_content)
    print("File written successfully")
    
