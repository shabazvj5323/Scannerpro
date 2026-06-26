import yfinance as yf
from concurrent.futures import ThreadPoolExecutor

with open('tickers.txt', 'r') as f:
    tickers = [line.strip() for line in f.readlines() if line.strip()]

def check_stock(ticker):
    try:
        df = yf.download(ticker, period='5d', interval='1d', progress=False)
        if len(df) < 5: return None
        # SIRF TEST: Koi filter nahi, bas pehle 5 stocks uthao
        return ticker
    except:
        return None

# Sirf pehle 10 stocks check karte hain
results = []
with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(check_stock, tickers[:10]))

s3_list = [r for r in results if r is not None]

# UI mein dikha do
html_content = f"<html><body><h2>TEST (First 10 Stocks):</h2><ul>" + "".join([f"<li>{s}</li>" for s in s3_list]) + "</ul></body></html>"
with open("index.html", "w") as f: f.write(html_content)
    
