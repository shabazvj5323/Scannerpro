import yfinance as yf
import os
from datetime import datetime
import pytz

# File Path fix
base_path = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(base_path, 'tickers.txt')

with open(file_path, 'r') as f:
    tickers = [line.strip() for line in f.readlines() if line.strip()]

results = []
# Sirf pehle 50 stocks check karte hain taaki timeout na ho
for t in tickers[:50]: 
    try:
        df = yf.download(t, period='5d', interval='1d', progress=False)
        if not df.empty:
            results.append(t)
    except:
        continue

# HTML update
html_content = f"""
<html><body>
<h2>Scanning Status: {len(results)} Stocks Found</h2>
<ul>{''.join([f'<li>{s}</li>' for s in results])}</ul>
<p>Last Update: {datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%d-%m %H:%M:%S")}</p>
</body></html>
"""
with open("index.html", "w") as f: f.write(html_content)
    
