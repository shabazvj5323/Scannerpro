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
        df = yf.download(ticker, period='5d', interval='5m', progress=False, auto_adjust=True)

        if df is None or df.empty:
            return None

        # FIX: yfinance kabhi-kabhi MultiIndex columns deta hai even for single ticker
        if isinstance(df.columns, type(df.columns)) and hasattr(df.columns, 'nlevels') and df.columns.nlevels > 1:
            df.columns = df.columns.get_level_values(0)

        if len(df) < 50:
            return None

        df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
        df['EMA30'] = df['Close'].ewm(span=30, adjust=False).mean()
        df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()

        c = df.iloc[-1]   # Latest Candle (Live ya Last Close)
        p = df.iloc[-2]   # Previous Candle

        # S1: Live Momentum (Current candle)
        s1 = bool((c['EMA20'] > c['EMA30'] > c['EMA50']) and (c['Volume'] > p['Volume'] * 1.5))

        # S2: Last Closing data
        s2 = bool(p['EMA20'] > p['EMA30'] > p['EMA50'])

        # S3: Crossover hone wala hai
        s3 = bool(abs(c['EMA20'] - c['EMA30']) < (c['Close'] * 0.002))

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
