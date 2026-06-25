name: Hourly Scanner
on:
  push:
  schedule:
    - cron: '0 * * * *'
  workflow_dispatch:

permissions:
  contents: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install yfinance pandas
      - name: Run Scanner
        run: python scanner.py
      - name: Commit and Push
        run: |
          git config --global user.name 'bot'
          git config --global user.email 'bot@email.com'
          git add index.html
          git commit -m "Update hourly stocks" || echo "No changes"
          git push
