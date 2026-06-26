import yfinance as yf
import os
from datetime import datetime
import pytz
from concurrent.futures import ThreadPoolExecutor

base_path = os.getcwd()
tickers_path = os.path.join(base_path, 'tickers.txt')

with open(tickers_path, 'r') as f:
    tickers = [line.strip() for line in f.readlines() if line.strip()]

def check_stock(ticker):
    try:
        df = yf.download(ticker, period='2d', interval='5m', progress=False)
        if len(df) < 50: return None
        
        # EMA Calculations
        df['EMA20'] = df['Close'].ewm(span=20).mean()
        df['EMA30'] = df['Close'].ewm(span=30).mean()
        df['EMA50'] = df['Close'].ewm(span=50).mean()
        
        current = df.iloc[-1]
        previous = df.iloc[-2]
        
        # LOGIC:
        # 1. 20 > 30 > 50 EMA Alignment
        # 2. Volume Spike: Current Volume > 1.5x Previous Volume
        ema_aligned = (current['EMA20'] > current['EMA30'] > current['EMA50'])
        volume_spike = (current['Volume'] > (previous['Volume'] * 1.5))
        
        s1 = ema_aligned and volume_spike
        return {'ticker': ticker, 's1': s1}
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
<h3>🎯 3-EMA (20>30>50) + Volume Spike</h3>
<ul>{get_html_list('s1')}</ul>
<p>Last Update: {datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%d-%m %H:%M:%S")}</p>
</body>
</html>
"""

with open(os.path.join(base_path, "index.html"), "w") as f:
    f.write(html_content)
    
