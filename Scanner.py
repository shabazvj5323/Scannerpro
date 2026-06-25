import yfinance as yf
import pandas as pd

# Apne stocks yahan add karo
tickers = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "SBIN.NS", "SAKSOFT.NS"]

def get_signals():
    signals = []
    for ticker in tickers:
        try:
            df = yf.download(ticker, period="5d", interval="5m")
            if df.empty: continue
            
            df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
            df['EMA30'] = df['Close'].ewm(span=30, adjust=False).mean()
            df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
            df['Vol_SMA'] = df['Volume'].rolling(20).mean()
            
            last = df.iloc[-1]
            if (last['EMA20'] > last['EMA30'] > last['EMA50']) and (last['Volume'] > last['Vol_SMA'] * 1.5):
                signals.append(ticker)
        except: continue
    return signals

def update_html(stocks):
    html = f"<html><head><meta http-equiv='refresh' content='300'><title>Stock Scanner</title></head><body><h1>🔥 Stocks with EMA Crossover</h1><ul>"
    for s in stocks: html += f"<li>{s}</li>"
    if not stocks: html += "<li>Koi stock match nahi hua.</li>"
    html += "</ul><p>Last Update: Hourly</p></body></html>"
    with open("index.html", "w") as f: f.write(html)

if __name__ == "__main__":
    stocks = get_signals()
    update_html(stocks)
  
