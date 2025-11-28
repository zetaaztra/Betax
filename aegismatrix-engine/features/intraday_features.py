"""
Intraday feature engineering (5m or 15m data).
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


def build_today_direction_features(intraday: pd.DataFrame, previous_close: float) -> dict:
    """
    Extract intraday context for Today Direction tile.
    
    Args:
        intraday: Intraday OHLCV DataFrame (5m or 15m), can be empty
        previous_close: Previous day close price
        
    Returns:
        Dict with gap_pct, realized_vol, orb_breakout_score, etc.
    """
    intraday = intraday.copy()
    
    # Handle empty intraday data
    if len(intraday) == 0:
        return {
            "gap_pct": 0.0,
            "realized_vol": 0.0,
            "orb_breakout_score": 0.5,
            "intraday_volatility_score": 0.0,
        }
    
    # Gap
    first_price = intraday["Open"].iloc[0]
    gap_pct = (first_price - previous_close) / previous_close if previous_close > 0 else 0
    
    # Returns
    intraday["ret"] = intraday["Close"].pct_change()
    
    # Realized volatility (morning only, first ~4 hours)
    morning_cutoff = min(len(intraday), 48)  # ~4 hours of 5m candles
    morning_returns = intraday["ret"].iloc[:morning_cutoff]
    realized_vol = morning_returns.std() if len(morning_returns) > 0 else 0
    
    # Open Range Breakout (first N candles)
    orb_candles = min(len(intraday), 12)  # first hour
    orb_high = intraday["High"].iloc[:orb_candles].max() if orb_candles > 0 else 0
    orb_low = intraday["Low"].iloc[:orb_candles].min() if orb_candles > 0 else 0
    
    current_price = intraday["Close"].iloc[-1]
    orb_range = orb_high - orb_low
    orb_breakout_score = 0.0
    
    if orb_range > 0:
        dist_to_high = orb_high - current_price
        dist_to_low = current_price - orb_low
        if dist_to_high < 0:  # Above ORB high
            orb_breakout_score = min(1.0, abs(dist_to_high) / orb_range * 2)
        elif dist_to_low < 0:  # Below ORB low
            orb_breakout_score = min(1.0, abs(dist_to_low) / orb_range * 2)
    
    return {
        "gap_pct": float(gap_pct),
        "realized_vol": float(realized_vol),
        "orb_breakout_score": float(orb_breakout_score),
        "realized_vol_norm": float(min(1.0, realized_vol / 0.05)),  # normalize
    }


def build_gamma_window_features(intraday: pd.DataFrame) -> list[dict]:
    """
    Split session into windows and compute vol score per window.
    
    Args:
        intraday: Intraday OHLCV
        
    Returns:
        List of {"window": "HH:MM-HH:MM", "score": 0-1}
    """
    intraday = intraday.copy()
    
    # Only consider trading hours: 09:15 to 15:30 (6 hours 15 min)
    # Split into meaningful windows based on typical market behavior
    
    windows = [
        ("09:15-09:45", 0, 6),    # Opening 30 min (most volatile)
        ("09:45-10:45", 6, 12),   # Morning continuation (1 hour)
        ("10:45-12:00", 18, 15),  # Late morning (1h 15min)
        ("12:00-14:00", 33, 24),  # Afternoon lull (2 hours)
        ("14:00-15:00", 57, 12),  # Pre-closing (1 hour)
        ("15:00-15:30", 69, 6),   # Final push (30 min)
    ]
    
    intraday["ret"] = intraday["Close"].pct_change()
    session_vol = intraday["ret"].std()
    
    results = []
    
    for label, start_idx, num_candles in windows:
        end_idx = start_idx + num_candles
        
        if end_idx <= len(intraday):
            window_data = intraday.iloc[start_idx:end_idx]
            window_vol = window_data["ret"].std()
            
            # Normalize score
            score = min(1.0, window_vol / (session_vol + 1e-6))
            
            results.append({
                "window": label,
                "score": float(score)
            })
    
    logger.info(f"Built gamma window features: {len(results)} windows")
    return results
