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
        # Puraana data aur naya data dono lene ke liye '5d' best hai
        df = yf.download(ticker, period='5d', interval='5m', progress=False)
        if len(df) < 50: return None
        
        df['EMA20'] = df['Close'].ewm(span=20).mean()
        df['EMA30'] = df['Close'].ewm(span=30).mean()
        df['EMA50'] = df['Close'].ewm(span=50).mean()
        
        c = df.iloc[-1]   # Latest Candle (Live ya Last Close)
        p = df.iloc[-2]   # Previous Candle
        
        # S1: Live Momentum (Current candle)
        s1 = (c['EMA20'] > c['EMA30'] > c['EMA50']) and (c['Volume'] > p['Volume'] * 1.5)
        
        # S2: Last Closing data (Pichli 3 candles ka average trend)
        s2 = (p['EMA20'] > p['EMA30'] > p['EMA50'])
        
        # S3: Crossover Hone wala hai (20 aur 30 EMA ka gap < 0.1%)
        s3 = abs(c['EMA20'] - c['EMA30']) < (c['Close'] * 0.001)
        
        return {'ticker': ticker, 's1': s1, 's2': s2, 's3': s3}
    except:
        return None

with ThreadPoolExecutor(max_workers=10) as executor:
    results = [res for res in executor.map(check_stock, tickers) if res is not None]

def get_list(key):
    filtered = [r['ticker'] for r in results if r[key]]
    return "".join([f'<li>{s.replace(".NS", "")}</li>' for s in filtered]) if filtered else "<li>Searching...</li>"

html = f"""
<html>
<body>
<h3>🚀 S1: Live Momentum / Last Close</h3><ul>{get_list('s1')}</ul>
<hr>
<h3>📅 S2: Last Closing Trend</h3><ul>{get_list('s2')}</ul>
<hr>
<h3>⏳ S3: Crossover Near Future</h3><ul>{get_list('s3')}</ul>
<p>Update: {datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%d-%m %H:%M")}</p>
</body>
</html>
"""
with open("index.html", "w") as f: f.write(html)
    
