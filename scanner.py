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

        # FIX: proper MultiIndex flatten check
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        if len(df) < 50:
            return None

        close = df['Close']
        volume = df['Volume']

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

        # S1: Live Momentum (current candle, trend + volume spike)
        s1 = bool((c_e20 > c_e30 > c_e50) and (c_vol > p_vol * 1.5))

        # S2: Last Closing Trend (previous closed candle)
        s2 = bool(p_e20 > p_e30 > p_e50)

        # S3: Crossover Near Future (EMA20-30 gap < 0.2%)
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
    if not filtered:
        return '<p class="empty">No match right now</p>'

    items = ""
    for s in filtered:
        symbol = s.replace(".NS", "")
        url = f"https://kite.zerodha.com/chart/ext/tvc/NSE/{symbol}"
        items += f'<a class="chip" href="{url}" target="_blank">{symbol}</a>'
    return f'<div class="chips">{items}</div>'

html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>EMA Scanner</title>
<style>
* {{ box-sizing: border-box; }}
body {{
    margin: 0;
    padding: 16px;
    background: #0d1117;
    color: #e6edf3;
    font-family: -apple-system, Segoe UI, Roboto, Arial, sans-serif;
}}
.header {{
    margin-bottom: 20px;
}}
.header h1 {{
    font-size: 22px;
    margin: 0 0 4px 0;
    color: #58a6ff;
}}
.header p {{
    margin: 0;
    color: #8b949e;
    font-size: 13px;
}}
.card {{
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 16px;
}}
.card-title {{
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 12px;
}}
.count {{
    background: #1f6feb;
    color: white;
    font-size: 12px;
    padding: 2px 8px;
    border-radius: 10px;
    margin-left: auto;
}}
.chips {{
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}}
.chip {{
    background: #21262d;
    border: 1px solid #30363d;
    color: #58a6ff;
    text-decoration: none;
    padding: 6px 12px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
    transition: background 0.15s;
}}
.chip:active {{
    background: #1f6feb;
    color: white;
}}
.empty {{
    color: #6e7681;
    font-style: italic;
    font-size: 14px;
    margin: 0;
}}
.footer {{
    text-align: center;
    color: #6e7681;
    font-size: 12px;
    margin-top: 20px;
}}
.s1 .card-title {{ color: #f85149; }}
.s2 .card-title {{ color: #3fb950; }}
.s3 .card-title {{ color: #d29922; }}
</style>
</head>
<body>

<div class="header">
    <h1>📊 EMA Scanner</h1>
    <p>Nifty 500 • Tap any stock to view Zerodha chart</p>
</div>

<div class="card s1">
    <div class="card-title">🚀 Live Momentum <span class="count">{len([r for r in results if r['s1']])}</span></div>
    {get_list('s1')}
</div>

<div class="card s2">
    <div class="card-title">📅 Last Closing Trend <span class="count">{len([r for r in results if r['s2']])}</span></div>
    {get_list('s2')}
</div>

<div class="card s3">
    <div class="card-title">⏳ Crossover Near Future <span class="count">{len([r for r in results if r['s3']])}</span></div>
    {get_list('s3')}
</div>

<div class="footer">
    Update: {datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%d-%m %H:%M")} IST<br>
    Processed: {len(results)} / {len(tickers)} tickers
</div>

</body>
</html>
"""
with open("index.html", "w") as f:
    f.write(html)
