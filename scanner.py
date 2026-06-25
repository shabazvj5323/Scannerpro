import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz
from concurrent.futures import ThreadPoolExecutor

# Nifty 500 symbols (Top companies)
# Main aapko ek sample list de raha hun, aap isse expand kar sakte hain
tickers = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS', 'LT.NS', 'ITC.NS', 'AXISBANK.NS', 'KOTAKBANK.NS', 'BHARTIARTL.NS', 'TATASTEEL.NS', 'WIPRO.NS', 'HCLTECH.NS', 'SUNPHARMA.NS'] # Add more here...

def check_stock(ticker):
    try:
        df = yf.download(ticker, period='2mo', interval='1d', progress=False)
        if len(df) < 50: return None
        
        df['EMA20'] = df['Close'].ewm(span=20).mean()
        df['EMA30'] = df['Close'].ewm(span=30).mean()
        df['EMA50'] = df['Close'].ewm(span=50).mean()
        df['Vol_SMA'] = df['Volume'].rolling(window=10).mean()
        
        last = df.iloc[-1]
        
        if (last['EMA20'] > last['EMA30'] > last['EMA50']) and (last['Volume'] > last['Vol_SMA'] * 1.10):
            return ticker
    except:
        return None

# Threading use kar rahe hain taaki 500 stocks jaldi scan ho
signals = []
with ThreadPoolExecutor(max_workers=10) as executor:
    results = executor.map(check_stock, tickers)
    signals = [r for r in results if r is not None]

ist = pytz.timezone('Asia/Kolkata')
update_time = datetime.now(ist).strftime("%d-%m-%Y %H:%M:%S IST")

html_content = f"""
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: sans-serif; padding: 15px; background: #f0f2f5; }}
        .card {{ background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        h2 {{ color: #d32f2f; }}
        li {{ padding: 10px; border-bottom: 1px solid #eee; font-weight: bold; color: #2e7d32; }}
    </style>
</head>
<body>
    <div class="card">
        <h2>🔥 Nifty 500 Scanner</h2>
        {'<ul>' + ''.join([f'<li>✅ {s}</li>' for s in signals]) + '</ul>' if signals else '<p>• No signals found.</p>'}
        <div style="font-size:10px; color:#888; margin-top:15px;">Last Update: {update_time}</div>
    </div>
</body>
</html>
"""
with open("index.html", "w") as f: f.write(html_content)
    
