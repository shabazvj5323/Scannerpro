import yfinance as yf
import os
import pandas as pd
from datetime import datetime
import pytz
from concurrent.futures import ThreadPoolExecutor

base_path = os.getcwd()
tickers_path = os.path.join(base_path, 'tickers.txt')

with open(tickers_path, 'r') as f:
    tickers = [line.strip() for line in f.readlines() if line.strip()]

def check_stock(ticker):
    try:
        df = yf.download(ticker, period='5d', interval='5m', progress=False, auto_adjust=True)

        if df is None or df.empty:
            return None

        # FIX: proper MultiIndex flatten check using pandas isinstance
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        if len(df) < 50:
            return None

        close = df['Close']
        volume = df['Volume']

        # Agar still Series nahi hai (DataFrame hai), to squeeze kar do
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]
        if isinstance(volume, pd.DataFrame):
            volume = volume.iloc[:, 0]

        ema20 = close.ewm(span=20, adjust=False).mean()
        ema30 = close.ewm(span=30, adjust=False).mean()
        ema50 = close.ewm(span=50, adjust=False).mean()

        c_close = close.iloc[-1]
        c_vol = volume.iloc[-1]
        p_vol = volume.iloc[-2]

        c_e20, c_e30, c_e50 = ema20.iloc[-1], ema30.iloc[-1], ema50.iloc[-1]
        p_e20, p_e30, p_e50 = ema20.iloc[-2], ema30.iloc[-2], ema50.iloc[-2]

        s1 = bool((c_e20 > c_e30 > c_e50) and (c_vol > p_vol * 1.5))
        s2 = bool(p_e20 > p_e30 > p_e50)
        s3 = bool(abs(c_e20 - c_e30) < (c_close * 0.002))

        return {'ticker': ticker, 's1': s1, 's2': s2, 's3': s3}
    except Exception as e:
        print(f"Error on {ticker}: {e}")
        return None

with ThreadPoolExecutor(max_workers=10) as executor:
    results = [res for res in executor.map(check_stock, tickers) if res is not None]

print(f"Total tickers processed successfully: {len(results)} / {len(tickers)}")

def get_list(key):
    filtered = [r['ticker'] for r in results if r[key]]
    return "".join([f'<li>{s.replace(".NS", "")}</li>' for s in filtered]) if filtered else "<li>No match right now</li>"

html = f"""
<html>
<body>
<h3>🚀 S1: Live Momentum / Last Close</h3><ul>{get_list('s1')}</ul>
<hr>
<h3>📅 S2: Last Closing Trend</h3><ul>{get_list('s2')}</ul>
<hr>
<h3>⏳ S3: Crossover Near Future</h3><ul>{get_list('s3')}</ul>
<p>Update: {datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%d-%m %H:%M")}</p>
<p>Processed: {len(results)} / {len(tickers)} tickers</p>
</body>
</html>
"""
with open("index.html", "w") as f:
    f.write(html)
