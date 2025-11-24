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


def get_daily_history(symbol: str, years: int = LOOKBACK_YEARS, force_refresh: bool = False) -> pd.DataFrame:
    """
    Fetch daily OHLCV history for a symbol.
    Checks local CSV cache first. If cache is stale or missing, fetches from API and updates cache.
    
    Args:
        symbol: Ticker symbol (e.g., "^NSEI")
        years: Lookback period in years
        force_refresh: If True, ignore cache and force API fetch
        
    Returns:
        DataFrame with OHLCV data, sorted by date
    """
    # Ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Sanitize symbol for filename
    safe_symbol = symbol.replace("^", "").replace(":", "_")
    cache_path = DATA_DIR / f"{safe_symbol}_daily.csv"
    
    cached_df = pd.DataFrame()
    cache_valid = False
    
    # Try to load from cache
    if cache_path.exists() and not force_refresh:
        try:
            cached_df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
            if not cached_df.empty:
                last_date = cached_df.index[-1].date()
                today = datetime.now().date()
                
                # If data is from today, we consider it fresh enough
                # (For a real production system, we'd check market close time, but this is sufficient)
                if last_date >= today:
                    logger.info(f"Cache hit for {symbol}: Data up to {last_date} is fresh.")
                    cache_valid = True
                else:
                    logger.info(f"Cache stale for {symbol}: Last date {last_date}, today {today}. Will try to update.")
        except Exception as e:
            logger.warning(f"Failed to read cache for {symbol}: {e}")
            
    if cache_valid:
        return cached_df

    # If we are here, we need to fetch data (either no cache, stale cache, or force_refresh)
    end = datetime.today()
    start = end - timedelta(days=365 * years)
    
    logger.info(f"Fetching daily history for {symbol} from {start.date()} to {end.date()}")
    
    fetched_df = pd.DataFrame()
    fetch_success = False
    
    # Try direct API first
    try:
        fetched_df = _fetch_yahoo_api_data(symbol, start_date=start, end_date=end, interval="1d")
        if not fetched_df.empty:
            fetch_success = True
    except Exception as e:
        logger.warning(f"Direct API fetch failed for {symbol}: {e}")

    # Fallback to yfinance if direct API failed
    if not fetch_success:
        try:
            logger.info(f"Falling back to yfinance for {symbol}")
            fetched_df = yf.download(symbol, start=start, end=end, progress=False, timeout=30)
            
            # Handle MultiIndex columns (yfinance update)
            if isinstance(fetched_df.columns, pd.MultiIndex):
                fetched_df.columns = fetched_df.columns.get_level_values(0)
                
            fetched_df = fetched_df.dropna()
            if not fetched_df.empty:
                fetch_success = True
                logger.info(f"Downloaded {len(fetched_df)} daily candles for {symbol} via yfinance")
        except Exception as e:
            logger.error(f"Error fetching {symbol} via yfinance: {e}")

    # Decide what to return
    if fetch_success and not fetched_df.empty:
        # Save to cache
        try:
            fetched_df.to_csv(cache_path)
            logger.info(f"Saved {len(fetched_df)} rows to cache: {cache_path}")
        except Exception as e:
            logger.error(f"Failed to save cache for {symbol}: {e}")
        return fetched_df
    
    # If fetch failed but we have stale cache, return that as fallback
    if not cached_df.empty:
        logger.warning(f"Fetch failed for {symbol}, returning stale cache (last date: {cached_df.index[-1].date()})")
        return cached_df
        
    # If everything failed
    if not fetch_success:
        logger.error(f"Failed to fetch data for {symbol} and no cache available.")
        # Raise if it was a yfinance error that bubbled up, or return empty
        # The original code raised on yfinance error, so we should probably raise or return empty.
        # Returning empty allows the caller to handle it.
        return pd.DataFrame()
        
    return pd.DataFrame()


def get_intraday_history(
    symbol: str, period: str = INTRADAY_PERIOD, interval: str = INTRADAY_INTERVAL, force_refresh: bool = False
) -> pd.DataFrame:
    """
    Fetch intraday OHLCV history.
    Checks local CSV cache first.
    
    Args:
        symbol: Ticker symbol
        period: Period string (e.g., "5d")
        interval: Interval string (e.g., "5m")
        force_refresh: If True, ignore cache
        
    Returns:
        DataFrame with intraday OHLCV data
    """
    # Ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Sanitize symbol for filename
    safe_symbol = symbol.replace("^", "").replace(":", "_")
    cache_path = DATA_DIR / f"{safe_symbol}_intraday.csv"
    
    cached_df = pd.DataFrame()
    cache_valid = False
    
    # Try to load from cache
    if cache_path.exists() and not force_refresh:
        try:
            cached_df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
            if not cached_df.empty:
                # Check if cache is recent (e.g. modified within last 15 mins)
                # For intraday, "freshness" is more strict. 
                # But if we are rate limited, we definitely want the cache.
                mtime = datetime.fromtimestamp(cache_path.stat().st_mtime)
                if datetime.now() - mtime < timedelta(minutes=15):
                    logger.info(f"Intraday cache hit for {symbol}: {mtime}")
                    cache_valid = True
                else:
                    logger.info(f"Intraday cache stale for {symbol}: {mtime}")
        except Exception as e:
            logger.warning(f"Failed to read intraday cache for {symbol}: {e}")
            
    if cache_valid:
        return cached_df

    logger.info(f"Fetching intraday history for {symbol} (period={period}, interval={interval})")
    
    fetched_df = pd.DataFrame()
    fetch_success = False
    
    # Try direct API first
    try:
        fetched_df = _fetch_yahoo_api_data(symbol, period=period, interval=interval)
        if not fetched_df.empty:
            fetch_success = True
    except Exception as e:
        logger.warning(f"Direct API intraday fetch failed for {symbol}: {e}")
        
    if not fetch_success:
        try:
            # Fallback to yfinance
            logger.info(f"Falling back to yfinance for intraday {symbol}")
            ticker = yf.Ticker(symbol)
            fetched_df = ticker.history(period=period, interval=interval, auto_adjust=False)
            
            if fetched_df.empty:
                logger.warning(f"No intraday data for {symbol}, trying alternative period")
                # Try 1d as fallback
                fetched_df = ticker.history(period="1d", interval=interval, auto_adjust=False)
            
            fetched_df = fetched_df.dropna()
            if not fetched_df.empty:
                fetch_success = True
                logger.info(f"Downloaded {len(fetched_df)} intraday candles for {symbol}")
        except Exception as e:
            logger.error(f"Error fetching intraday {symbol}: {e}")
            
    # Decide what to return
    if fetch_success and not fetched_df.empty:
        # Save to cache
        try:
            fetched_df.to_csv(cache_path)
            logger.info(f"Saved {len(fetched_df)} intraday rows to cache: {cache_path}")
        except Exception as e:
            logger.error(f"Failed to save intraday cache for {symbol}: {e}")
        return fetched_df
    
    # If fetch failed but we have stale cache, return that as fallback
    if not cached_df.empty:
        logger.warning(f"Intraday fetch failed for {symbol}, returning stale cache")
        return cached_df

    # If everything failed
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
    Get live/current price with multiple fallback strategies.
    Prioritizes: 1) Intraday 1m data, 2) Info, 3) Fast_info, 4) Historical 1m
    
    Args:
        symbol: Ticker symbol (e.g., "^NSEI")
        
    Returns:
        Current price as float or None if all methods fail
    """
    try:
        ticker = yf.Ticker(symbol)
        
        # First priority: 1-minute intraday data (most recent during market hours)
        try:
            hist_1m = ticker.history(period="1d", interval="1m", auto_adjust=False)
            if not hist_1m.empty:
                price = float(hist_1m["Close"].iloc[-1])
                if price > 0:
                    logger.info(f"Got live price for {symbol} from 1-min intraday: {price}")
                    return price
        except Exception as e:
            logger.debug(f"1-minute history fetch failed for {symbol}: {e}")
        
        # Second priority: info (tick data during market hours)
        try:
            info = ticker.info
            price = info.get("regularMarketPrice") or info.get("currentPrice") or info.get("previousClose")
            if price and price > 0:
                logger.info(f"Got live price for {symbol} from info: {price}")
                return float(price)
        except Exception as e:
            logger.debug(f"Info fetch failed for {symbol}: {e}")
        
        # Third priority: fast_info
        try:
            fast_info = ticker.fast_info
            price = fast_info.get("lastPrice") or fast_info.get("regularMarketPrice")
            if price and price > 0:
                logger.info(f"Got live price for {symbol} from fast_info: {price}")
                return float(price)
        except Exception as e:
            logger.debug(f"Fast_info fetch failed for {symbol}: {e}")
        
        # Fallback: 5-minute data
        try:
            hist_5m = ticker.history(period="5d", interval="5m", auto_adjust=False)
            if not hist_5m.empty:
                price = float(hist_5m["Close"].iloc[-1])
                if price > 0:
                    logger.info(f"Got live price for {symbol} from 5-min data: {price}")
                    return price
        except Exception as e:
            logger.debug(f"5-minute history fetch failed for {symbol}: {e}")
        
        logger.warning(f"Could not get live price for {symbol} through any method")
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
