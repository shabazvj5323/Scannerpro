import yfinance as yf
import pandas as pd

# Apne stocks ki list yahan update kar sakte ho
tickers = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "SBIN.NS", "SAKSOFT.NS", "HDFCBANK.NS"]

def get_signals():
    signals = []
    for ticker in tickers:
        try:
            # 5-minute ka data fetch karo
            df = yf.download(ticker, period="5d", interval="5m", progress=False)
            if df.empty: continue
            
            # EMA calculations
            df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
            df['EMA30'] = df['Close'].ewm(span=30, adjust=False).mean()
            df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
            df['Vol_SMA'] = df['Volume'].rolling(20).mean()
            
            last = df.iloc[-1]
            
            # Strategy: EMA alignment aur Volume Spike
            if (last['EMA20'] > last['EMA30'] > last['EMA50']) and (last['Volume'] > last['Vol_SMA'] * 1.5):
                signals.append(ticker)
        except:
            continue
    return signals

def update_html(stocks):
    html = f"""
    <html>
    <head>
        <meta http-equiv='refresh' content='300'>
        <style>body {{ font-family: Arial; padding: 20px; }} h1 {{ color: #2c3e50; }} li {{ font-size: 20px; color: green; }}</style>
    </head>
    <body>
        <h1>🔥 Live Stock Signals</h1>
        <ul>{''.join([f'<li>{s}</li>' for s in stocks]) if stocks else '<li>Koi stock match nahi hua.</li>'}</ul>
        <p>Last Update: {pd.Timestamp.now()}</p>
    </body>
    </html>
    """
    with open("index.html", "w") as f: f.write(html)

if __name__ == "__main__":
    stocks = get_signals()
    update_html(stocks)
    
