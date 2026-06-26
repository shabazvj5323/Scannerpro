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

VOLUME_MULTIPLIER = 5   # current volume kam se kam 5x pichle candle se zyada ho

def check_stock(ticker):
    try:
        df = yf.download(ticker, period='5d', interval='5m', progress=False, auto_adjust=True)

        if df is None or df.empty:
            return None

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        if len(df) < 50:
            return None

        close = df['Close']
        open_ = df['Open']
        volume = df['Volume']

        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]
        if isinstance(open_, pd.DataFrame):
            open_ = open_.iloc[:, 0]
        if isinstance(volume, pd.DataFrame):
            volume = volume.iloc[:, 0]

        ema20 = close.ewm(span=20, adjust=False).mean()
        ema30 = close.ewm(span=30, adjust=False).mean()
        ema50 = close.ewm(span=50, adjust=False).mean()

        # Current (latest) candle
        c_open, c_close = open_.iloc[-1], close.iloc[-1]
        c_vol, p_vol = volume.iloc[-1], volume.iloc[-2]
        c_e20, c_e30, c_e50 = ema20.iloc[-1], ema30.iloc[-1], ema50.iloc[-1]

        # Previous candle (to detect fresh crossover)
        p_e20, p_e30, p_e50 = ema20.iloc[-2], ema30.iloc[-2], ema50.iloc[-2]

        # Condition 1: Abhi alignment bana hai (current candle), pehle nahi tha
        aligned_now = c_e20 > c_e30 > c_e50
        aligned_before = p_e20 > p_e30 > p_e50
        fresh_crossover = aligned_now and not aligned_before

        # Condition 2: Solid bullish candle
        bullish = c_close > c_open

        # Condition 3: Volume spike (current vs previous candle)
        volume_spike = p_vol > 0 and c_vol > (p_vol * VOLUME_MULTIPLIER)

        match = bool(fresh_crossover and bullish and volume_spike)

        if match:
            return {
                'ticker': ticker,
                'close': round(float(c_close), 2),
                'cur_vol': int(c_vol),
                'prev_vol': int(p_vol)
            }
        return None

    except Exception as e:
        print(f"Error on {ticker}: {e}")
        return None

with ThreadPoolExecutor(max_workers=10) as executor:
    raw_results = list(executor.map(check_stock, tickers))

results = [r for r in raw_results if r is not None]

print(f"Matches found: {len(results)} / {len(tickers)} tickers scanned")

def get_list():
    if not results:
        return '<p class="empty">No match right now</p>'
    items = ""
    for r in results:
        symbol = r['ticker'].replace(".NS", "")
        url = f"https://www.tradingview.com/chart/?symbol=NSE:{symbol}"
        items += f'<a class="chip" href="{url}" target="_blank">{symbol} <span class="vol">₹{r["close"]} | Vol {r["cur_vol"]:,}</span></a>'
    return f'<div class="chips">{items}</div>'

html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>EMA Crossover Scanner</title>
<style>
* {{ box-sizing: border-box; }}
body {{
    margin: 0;
    padding: 16px;
    background: #0d1117;
    color: #e6edf3;
    font-family: -apple-system, Segoe UI, Roboto, Arial, sans-serif;
}}
.header h1 {{ font-size: 22px; margin: 0 0 4px 0; color: #58a6ff; }}
.header p {{ margin: 0; color: #8b949e; font-size: 13px; }}
.card {{
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 16px;
    margin-top: 20px;
}}
.chips {{ display: flex; flex-direction: column; gap: 10px; }}
.chip {{
    background: #21262d;
    border: 1px solid #3fb950;
    color: #3fb950;
    text-decoration: none;
    padding: 10px 14px;
    border-radius: 8px;
    font-size: 15px;
    font-weight: 600;
    display: flex;
    justify-content: space-between;
}}
.vol {{ color: #8b949e; font-size: 13px; font-weight: 400; }}
.empty {{ color: #6e7681; font-style: italic; font-size: 14px; }}
.footer {{ text-align: center; color: #6e7681; font-size: 12px; margin-top: 20px; }}
</style>
</head>
<body>

<div class="header">
    <h1>🚀 Fresh Bullish Crossover</h1>
    <p>EMA20&gt;30&gt;50 just crossed + Bullish candle + Volume spike (5x+)</p>
</div>

<div class="card">
    {get_list()}
</div>

<div class="footer">
    Update: {datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%d-%m %H:%M")} IST<br>
    Scanned: {len(tickers)} tickers
</div>

</body>
</html>
"""
with open("index.html", "w") as f:
    f.write(html)
