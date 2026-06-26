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
        # Hamein 15 candles chahiye logic ke liye
        df = yf.download(ticker, period='2d', interval='5m', progress=False)
        if len(df) < 50: return None
        
        df['EMA20'] = df['Close'].ewm(span=20).mean()
        df['EMA30'] = df['Close'].ewm(span=30).mean()
        df['EMA50'] = df['Close'].ewm(span=50).mean()
        
        c = df.iloc[-1] # Current candle
        
        # S1: Original Logic
        s1 = (c['EMA20'] > c['EMA30'] > c['EMA50']) and (c['Volume'] > df.iloc[-2]['Volume'] * 1.5)
        
        # S2: Hone wala hai (EMA20 aur 30 ka gap < 0.2%)
        gap = abs(c['EMA20'] - c['EMA30'])
        s2 = gap < (c['Close'] * 0.002) and (c['EMA20'] > c['EMA50'])
        
        # S3: Cross hoke 3 candle beet chuki hai (Fresh breakout)
        # Check kar rahe hain ki pichli 3 candles mein crossover hua tha
        s3 = (df.iloc[-3]['EMA20'] > df.iloc[-3]['EMA30']) 
        
        return {'ticker': ticker, 's1': s1, 's2': s2, 's3': s3}
    except:
        return None

with ThreadPoolExecutor(max_workers=10) as executor:
    results = [res for res in executor.map(check_stock, tickers) if res is not None]

def get_html_list(key):
    filtered = [r['ticker'] for r in results if r[key]]
    # "No signal" nahi dikhayenge agar list khali hai
    if not filtered: return "<li>Checking...</li>" 
    return "".join([f'<li><strong>{s.replace(".NS", "")}</strong></li>' for s in filtered])

html_content = f"""
<html><body>
<h3>🚀 S1: Current Momentum</h3><ul>{get_html_list('s1')}</ul>
<hr>
<h3>⏳ S2: Hone wala hai (Nazdik)</h3><ul>{get_html_list('s2')}</ul>
<hr>
<h3>✅ S3: Fresh Breakout (Last 3 Candles)</h3><ul>{get_html_list('s3')}</ul>
<p>Last Update: {datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%H:%M:%S")}</p>
</body></html>
"""
with open("index.html", "w") as f: f.write(html_content)
    
