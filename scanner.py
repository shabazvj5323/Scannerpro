import yfinance as yf
import pandas as pd
from datetime import datetime

# Yahan tumhare target stocks ki list hai (Ya Nifty 500 ke stocks)
tickers = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS'] 

signals = []

for ticker in tickers:
    df = yf.download(ticker, period='1mo', interval='1d')
    if len(df) < 50: continue
    
    # EMA Calculation
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA30'] = df['Close'].ewm(span=30).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()
    
    # Volume SMA (10 days)
    df['Vol_SMA'] = df['Volume'].rolling(window=10).mean()
    
    last = df.iloc[-1]
    
    # Tummhari Strategy: 10% volume growth (1.10)
    if (last['EMA20'] > last['EMA30'] > last['EMA50']) and (last['Volume'] > last['Vol_SMA'] * 1.10):
        signals.append(ticker)

# HTML Update
update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
if signals:
    content = f"<h3>🔥 Live Stock Signals</h3><ul>" + "".join([f"<li>{s}</li>" for s in signals]) + f"</ul><p>Last Update: {update_time}</p>"
else:
    content = f"<h3>🔥 Live Stock Signals</h3><p>• Koi stock match nahi hua.</p><p>Last Update: {update_time}</p>"

with open("index.html", "w") as f:
    f.write(content)
    
