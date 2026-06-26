import yfinance as yf
import os

base_path = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(base_path, 'tickers.txt'), 'r') as f:
    ticker = f.readline().strip() # Sirf pehla ticker uthao

df = yf.download(ticker, period='5d', interval='1d', progress=False)

# Debugging information
html_content = f"""
<html><body>
<h2>Debug Info</h2>
<p>Ticker: {ticker}</p>
<p>Data Received: {not df.empty}</p>
<p>Rows found: {len(df)}</p>
<pre>{df.tail(2).to_string() if not df.empty else "No Data"}</pre>
</body></html>
"""
with open("index.html", "w") as f: f.write(html_content)
    
