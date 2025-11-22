"""
Single entry point for market data via Yahoo Finance API.
Uses direct API calls when yfinance fails, with error handling and caching.
Falls back to NSE API for intraday/live data.
"""

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from pathlib import Path
import json
import logging
import sys
import requests
import time
import random
from typing import Optional, Tuple, Dict, Any

sys.path.insert(0, str(Path(__file__).parent))

from config import (
    NIFTY_SYMBOL,
    VIX_SYMBOL,
    LOOKBACK_YEARS,
    INTRADAY_PERIOD,
    INTRADAY_INTERVAL,
    DATA_DIR,
)

logger = logging.getLogger(__name__)

# NSE API endpoints for fallback
NSE_CHAIN_URL = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
NSE_HDR = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Referer": "https://www.nseindia.com/",
}

# Rotate User Agents to avoid blocking
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]


def _get_random_header() -> Dict[str, str]:
    """Get headers with a random user agent."""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }


def _fetch_nse_live_spot() -> Optional[float]:
    """
    Fetch live NIFTY spot price directly from NSE API.
    Fallback when yfinance intraday fails.
    
    Returns:
        Current spot price or None if failed
    """
    try:
        session = requests.Session()
        session.headers.update(NSE_HDR)
        
        # Establish session first
        session.get("https://www.nseindia.com", timeout=10)
        time.sleep(0.5)
        
        # Fetch option chain (has current spot)
        response = session.get(NSE_CHAIN_URL, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        spot = data.get("records", {}).get("underlyingValue")
        if spot and spot > 0:
            logger.info(f"Fetched live NSE spot: {spot}")
            return float(spot)
    except Exception as e:
        logger.debug(f"NSE spot fetch failed: {e}")
    
    return None


def _fetch_yahoo_api_data(
    symbol: str, 
    start_date: Optional[datetime] = None, 
    end_date: Optional[datetime] = None, 
    period: Optional[str] = None, 
    interval: str = "1d",
    retries: int = 3
) -> pd.DataFrame:
    """
    Fetch data directly from Yahoo Finance API with retries and robust error handling.
    Supports both historical (start/end) and range-based (period) fetching.
    
    Args:
        symbol: Ticker symbol (e.g., "^NSEI")
        start_date: Start date for historical data
        end_date: End date for historical data
        period: Range string (e.g., "5d", "1mo") - overrides start/end dates if provided
        interval: Data interval (e.g., "1d", "5m")
        retries: Number of retry attempts
        
    Returns:
        DataFrame with OHLCV data or empty DataFrame if failed
    """
    # Construct URL based on parameters
    if period:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval={interval}&range={period}"
    else:
        # Use timestamp range
        if start_date is None:
            start_date = datetime.now() - timedelta(days=365*LOOKBACK_YEARS)
        if end_date is None:
            end_date = datetime.now()
            
        start_ts = int(start_date.timestamp())
        end_ts = int(end_date.timestamp())
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval={interval}&period1={start_ts}&period2={end_ts}"
    
    for attempt in range(retries):
        try:
            headers = _get_random_header()
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 429:
                logger.warning(f"Rate limited by Yahoo (429). Waiting before retry {attempt+1}/{retries}...")
                time.sleep(2 * (attempt + 1))
                continue
                
            if response.status_code != 200:
                logger.warning(f"Yahoo API returned status {response.status_code} for {symbol}")
                continue
                
            data = response.json()
            
            if "chart" not in data or "result" not in data["chart"] or not data["chart"]["result"]:
                logger.warning(f"No data in API response for {symbol}")
                return pd.DataFrame()
            
            result = data["chart"]["result"][0]
            timestamps = result.get("timestamp", [])
            quotes = result.get("indicators", {}).get("quote", [{}])[0]
            
            if not timestamps or not quotes:
                logger.warning(f"Empty timestamps or quotes for {symbol}")
                return pd.DataFrame()
            
            df = pd.DataFrame({
                "Date": pd.to_datetime(timestamps, unit="s"),
                "Open": quotes.get("open", []),
                "High": quotes.get("high", []),
                "Low": quotes.get("low", []),
                "Close": quotes.get("close", []),
                "Volume": quotes.get("volume", []),
            })
            
            df = df.dropna()
            df.set_index("Date", inplace=True)
            
            if not df.empty:
                logger.info(f"Fetched {len(df)} rows from direct API for {symbol}")
                return df
                
        except requests.exceptions.RequestException as e:
            logger.debug(f"Attempt {attempt+1}/{retries} failed for {symbol}: {e}")
            time.sleep(1)
        except json.JSONDecodeError:
            logger.warning(f"Failed to decode JSON from Yahoo for {symbol}")
        except Exception as e:
            logger.error(f"Unexpected error fetching {symbol}: {e}")
            
    logger.error(f"Failed to fetch data for {symbol} after {retries} attempts")
    return pd.DataFrame()


def get_daily_history(symbol: str, years: int = LOOKBACK_YEARS) -> pd.DataFrame:
    """
    Fetch daily OHLCV history for a symbol.
    Tries direct API first, falls back to yfinance.
    
    Args:
        symbol: Ticker symbol (e.g., "^NSEI")
        years: Lookback period in years
        
    Returns:
        DataFrame with OHLCV data, sorted by date
    """
    end = datetime.today()
    start = end - timedelta(days=365 * years)
    
    logger.info(f"Fetching daily history for {symbol} from {start.date()} to {end.date()}")
    
    # Try direct API first
    df = _fetch_yahoo_api_data(symbol, start_date=start, end_date=end, interval="1d")
    if len(df) > 0:
        return df
    
    # Fallback to yfinance
    try:
        logger.info(f"Falling back to yfinance for {symbol}")
        df = yf.download(symbol, start=start, end=end, progress=False, timeout=30)
        df = df.dropna()
        logger.info(f"Downloaded {len(df)} daily candles for {symbol} via yfinance")
        return df
    except Exception as e:
        logger.error(f"Error fetching {symbol}: {e}")
        raise


def get_intraday_history(
    symbol: str, period: str = INTRADAY_PERIOD, interval: str = INTRADAY_INTERVAL
) -> pd.DataFrame:
    """
    Fetch intraday OHLCV history.
    Tries direct API first, falls back to yfinance.
    
    Args:
        symbol: Ticker symbol
        period: Period string (e.g., "5d")
        interval: Interval string (e.g., "5m")
        
    Returns:
        DataFrame with intraday OHLCV data
    """
    logger.info(f"Fetching intraday history for {symbol} (period={period}, interval={interval})")
    
    # Try direct API first
    df = _fetch_yahoo_api_data(symbol, period=period, interval=interval)
    if len(df) > 0:
        return df
        
    try:
        # Fallback to yfinance
        logger.info(f"Falling back to yfinance for intraday {symbol}")
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval, auto_adjust=False)
        
        if df.empty:
            logger.warning(f"No intraday data for {symbol}, trying alternative period")
            # Try 1d as fallback
            df = ticker.history(period="1d", interval=interval, auto_adjust=False)
        
        df = df.dropna()
        logger.info(f"Downloaded {len(df)} intraday candles for {symbol}")
        return df
    except Exception as e:
        logger.error(f"Error fetching intraday {symbol}: {e}")
        # Return empty dataframe instead of raising - allows pipeline to continue
        logger.warning(f"Intraday fetch failed, continuing with empty intraday data")
        return pd.DataFrame()


def get_vix_history(years: int = LOOKBACK_YEARS) -> pd.DataFrame:
    """
    Fetch India VIX daily history.
    
    Args:
        years: Lookback period in years
        
    Returns:
        DataFrame with VIX data
    """
    return get_daily_history(VIX_SYMBOL, years=years)


def get_live_price(symbol: str) -> float:
    """
    Get live/current price from yfinance ticker info.
    Real-time during market hours, close when market is closed.
    
    Args:
        symbol: Ticker symbol (e.g., "^NSEI")
        
    Returns:
        Current price as float
    """
    try:
        ticker = yf.Ticker(symbol)
        
        # Try info first (most reliable for live price)
        try:
            info = ticker.info
            price = info.get("regularMarketPrice") or info.get("currentPrice") or info.get("previousClose")
            if price and price > 0:
                logger.debug(f"Got live price for {symbol} from info: {price}")
                return float(price)
        except Exception as e:
            logger.debug(f"Info fetch failed for {symbol}: {e}")
        
        # Try fast_info
        try:
            fast_info = ticker.fast_info
            price = fast_info.get("lastPrice") or fast_info.get("regularMarketPrice")
            if price and price > 0:
                logger.debug(f"Got live price for {symbol} from fast_info: {price}")
                return float(price)
        except Exception as e:
            logger.debug(f"Fast_info fetch failed for {symbol}: {e}")
        
        # Fallback to latest 1-minute data
        try:
            hist_1m = ticker.history(period="1d", interval="1m", auto_adjust=False)
            if not hist_1m.empty:
                price = float(hist_1m["Close"].iloc[-1])
                logger.debug(f"Got live price for {symbol} from 1-min data: {price}")
                return price
        except Exception as e:
            logger.debug(f"1-minute history fetch failed for {symbol}: {e}")
        
        logger.warning(f"Could not get live price for {symbol}")
        return None
        
    except Exception as e:
        logger.error(f"Error getting live price for {symbol}: {e}")
        return None


def get_market_snapshots() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Get latest daily snapshots for NIFTY and VIX.
    
    Returns:
        Tuple of (nifty_df, vix_df)
    """
    nifty = get_daily_history(NIFTY_SYMBOL)
    vix = get_vix_history()
    return nifty, vix


def get_latest_values() -> dict:
    """
    Get latest spot and VIX values.
    
    Returns:
        Dict with latest_spot, latest_vix, prev_spot, prev_vix
    """
    nifty, vix = get_market_snapshots()
    
    return {
        "latest_spot": float(nifty["Close"].iloc[-1]),
        "prev_spot": float(nifty["Close"].iloc[-2]),
        "latest_vix": float(vix["Close"].iloc[-1]),
        "prev_vix": float(vix["Close"].iloc[-2]),
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test
    nifty, vix = get_market_snapshots()
    print(f"NIFTY latest close: {nifty['Close'].iloc[-1]}")
    print(f"VIX latest close: {vix['Close'].iloc[-1]}")
