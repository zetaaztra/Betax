
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import yfinance as yf
from data_fetcher import get_live_price, get_daily_history, get_intraday_history
import logging

logging.basicConfig(level=logging.INFO)

def test_vix():
    symbol = "^INDIAVIX"
    print(f"Testing VIX fetching for {symbol}...")

    # 1. Daily History (Current method)
    print("\n--- Method 1: Daily History (Current) ---")
    daily = get_daily_history(symbol, years=1, force_refresh=True)
    if not daily.empty:
        print(f"Latest Daily Close: {daily['Close'].iloc[-1]}")
        print(f"Latest Daily Date: {daily.index[-1]}")
    else:
        print("Daily history empty")

    # 2. Intraday History
    print("\n--- Method 2: Intraday History ---")
    intraday = get_intraday_history(symbol, force_refresh=True)
    if not intraday.empty:
        print(f"Latest Intraday Close: {intraday['Close'].iloc[-1]}")
        print(f"Latest Intraday Time: {intraday.index[-1]}")
    else:
        print("Intraday history empty")

    # 3. Live Price Helper
    print("\n--- Method 3: get_live_price Helper ---")
    live = get_live_price(symbol)
    print(f"Live Price: {live}")

    # 4. yfinance Ticker Info
    print("\n--- Method 4: Ticker Info ---")
    try:
        ticker = yf.Ticker(symbol)
        # fast_info
        print(f"Fast Info Last Price: {ticker.fast_info.last_price}")
        # regular info
        info = ticker.info
        print(f"Regular Market Price: {info.get('regularMarketPrice')}")
        print(f"Current Price: {info.get('currentPrice')}")
        print(f"Previous Close: {info.get('previousClose')}")
    except Exception as e:
        print(f"Ticker info failed: {e}")

if __name__ == "__main__":
    test_vix()
