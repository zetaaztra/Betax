"""
NSE Option Chain Fetcher - Fallback for intraday/current market data
When yfinance intraday fails, use direct NSE API as fallback
"""

import requests
import json
from pathlib import Path
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

NSE_CHAIN_URL = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
NSE_QUOTE_URL = "https://www.nseindia.com/api/quote-equity?symbol=NIFTY50"

HDR = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
}


def get_nse_option_chain(max_retries=2):
    """
    Fetch live NIFTY option chain data from NSE.
    Includes current spot price and volatility.
    
    Returns:
        dict with spot, vix, option chain data or None if failed
    """
    session = requests.Session()
    session.headers.update(HDR)
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Fetching NSE option chain (attempt {attempt+1}/{max_retries})...")
            
            # Establish session first
            session.get("https://www.nseindia.com", timeout=10)
            
            # Fetch option chain
            response = session.get(NSE_CHAIN_URL, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            records = data.get("records", {})
            spot = records.get("underlyingValue")
            
            if not spot or spot <= 0:
                logger.warning(f"Invalid spot price: {spot}")
                continue
            
            # Extract current stats
            stats = records.get("strikeLimits", {})
            chain_data = records.get("data", [])
            
            logger.info(f"✓ Got NSE data: Spot={spot}, Strikes={len(chain_data)}")
            
            return {
                "spot": spot,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "chain_size": len(chain_data),
                "raw_data": data
            }
            
        except Exception as e:
            logger.warning(f"NSE fetch failed (attempt {attempt+1}): {e}")
            if attempt < max_retries - 1:
                import time
                time.sleep(1)
    
    logger.error("Failed to fetch NSE option chain after retries")
    return None


def get_nse_quote():
    """
    Fetch NIFTY50 quote from NSE.
    
    Returns:
        dict with price, change, volume or None if failed
    """
    try:
        session = requests.Session()
        session.headers.update(HDR)
        
        logger.info("Fetching NSE quote...")
        
        # Establish session
        session.get("https://www.nseindia.com", timeout=10)
        
        response = session.get(NSE_QUOTE_URL, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if "pricebandupper" in data:
            logger.info(f"✓ Got NSE quote")
            return data
        
    except Exception as e:
        logger.warning(f"NSE quote fetch failed: {e}")
    
    return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("Testing NSE fallback...")
    chain = get_nse_option_chain()
    if chain:
        print(f"✓ Spot: {chain['spot']}")
        print(f"  Strikes in chain: {chain['chain_size']}")
    else:
        print("✗ Failed to fetch NSE data")
