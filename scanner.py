import yfinance as yf
import os
from datetime import datetime
import pytz
from concurrent.futures import ThreadPoolExecutor

base_path = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(base_path, 'tickers.txt'), 'r') as f:
    tickers = [line.strip() for line in f.readlines() if line.strip()]

def check_stock(ticker):
    try:
        # 3mo ka data lena zaroori hai EMA calculation ke liye
        df = yf.download(ticker, period='3mo', interval='1d', progress=False)
        if len(df) < 50: return None
        
        df['EMA20'] = df['Close'].ewm(span=20).mean()
        df['EMA30'] = df['Close'].ewm(span=30).mean()
        df['EMA50'] = df['Close'].ewm(span=50).mean()
        df['Vol_SMA'] = df['Volume'].rolling(window=10).mean()
        
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Strategies (Ab 50+ data points milenge toh calculation hogi)
        s1 = (last['EMA20'] > last['EMA30'] > last['EMA50']) and (last['Volume'] > last['Vol_SMA'] * 1.05)
        s2 = (last['EMA20'] > last['EMA50']) and (last['Volume'] > last['Vol_SMA'] * 1.05)
        s3 = (prev['EMA20'] > prev['EMA30'] > prev['EMA50']) and (prev['Volume'] > prev['Vol_SMA'] * 1.05)
        
        return {'ticker': ticker, 's1': s1, 's2': s2, 's3': s3}
    except:
        return None

with ThreadPoolExecutor(max_workers=20) as executor:
    results = [res for res in executor.map(check_stock, tickers) if res is not None]

def get_html(name, condition_key):
    filtered = [r['ticker'] for r in results if r[condition_key]]
    items = "".join([f'<li><a href="https://in.tradingview.com/chart/?symbol=NSE:{s.replace(".NS","")}" target="_blank">{s}</a></li>' for s in filtered])
    return f"<h3>{name} ({len(filtered)})</h3>" + (f"<ul>{items}</ul>" if filtered else "<p>No signals</p>")

html_content = f"<html><body>{get_html('🚀 Strategy 1 (Strict)', 's1')}<hr>{get_html('⚡ Strategy 2 (Loose)', 's2')}<hr>{get_html('📅 Strategy 3 (Yesterday)', 's3')}<p>Last Scan: {datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%d-%m %H:%M:%S')}</p></body></html>"
with open("index.html", "w") as f: f.write(html_content)
    
