"""
Daily feature engineering for all three engines.
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


def add_basic_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add basic technical features to daily OHLCV data.
    
    Args:
        df: DataFrame with OHLCV
        
    Returns:
        DataFrame with added features
    """
    df = df.copy()
    
    # Returns
    df["ret_1d"] = df["Close"].pct_change()
    df["ret_5d"] = df["Close"].pct_change(5)
    df["ret_10d"] = df["Close"].pct_change(10)
    df["ret_20d"] = df["Close"].pct_change(20)
    
    # Volatility
    df["vol_10d"] = df["ret_1d"].rolling(10).std()
    df["vol_20d"] = df["ret_1d"].rolling(20).std()
    df["vol_60d"] = df["ret_1d"].rolling(60).std()
    
    # ATR
    df["tr"] = np.maximum(
        df["High"] - df["Low"],
        np.maximum(
            abs(df["High"] - df["Close"].shift(1)),
            abs(df["Low"] - df["Close"].shift(1))
        )
    )
    df["atr_14"] = df["tr"].rolling(14).mean()
    
    # RSI
    df["delta"] = df["Close"].diff()
    gain = (df["delta"].where(df["delta"] > 0, 0)).rolling(window=14).mean()
    loss = (-df["delta"].where(df["delta"] < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df["rsi_14"] = 100 - (100 / (1 + rs))
    
    # EMA slopes
    df["ema_20"] = df["Close"].ewm(span=20).mean()
    df["ema_50"] = df["Close"].ewm(span=50).mean()
    df["ema_slope_20"] = (df["ema_20"] - df["ema_20"].shift(5)) / df["ema_20"]
    df["ema_slope_50"] = (df["ema_50"] - df["ema_50"].shift(5)) / df["ema_50"]
    
    return df


def build_direction_features(nifty: pd.DataFrame, vix: pd.DataFrame) -> pd.DataFrame:
    """
    Build feature matrix for direction engine.
    
    Args:
        nifty: Daily NIFTY OHLCV
        vix: Daily VIX OHLCV
        
    Returns:
        Feature DataFrame aligned to dates
    """
    nifty = add_basic_features(nifty).copy()
    vix = add_basic_features(vix).copy()
    
    # Rename VIX features to avoid conflict
    vix_cols = {col: f"vix_{col}" for col in vix.columns if col != "Close"}
    vix = vix.rename(columns=vix_cols)
    
    # Merge on date
    df = nifty.join(vix[["Close", "vix_vol_10d", "vix_vol_20d", "vix_vol_60d"]], rsuffix="_vix")
    df = df.dropna()
    
    # VIX percentile
    df["vix_percentile"] = df["Close_vix"].rolling(252).apply(
        lambda x: (x.iloc[-1] >= x).sum() / len(x)
    )
    
    logger.info(f"Built direction features: {df.shape}")
    return df


def build_seller_features(nifty: pd.DataFrame, vix: pd.DataFrame) -> pd.DataFrame:
    """
    Build feature matrix for seller engine.
    
    Args:
        nifty: Daily NIFTY OHLCV
        vix: Daily VIX OHLCV
        
    Returns:
        Feature DataFrame
    """
    # Same base as direction for now
    # Can extend with seller-specific metrics later
    df = build_direction_features(nifty, vix)
    
    # Tail metrics
    df["downside_tail"] = df["ret_1d"].rolling(20).apply(lambda x: x[x < 0].mean())
    df["upside_tail"] = df["ret_1d"].rolling(20).apply(lambda x: x[x > 0].mean())
    df["tail_asymmetry"] = (df["downside_tail"].abs() - df["upside_tail"].abs()) / (df["upside_tail"].abs() + 1e-6)
    
    logger.info(f"Built seller features: {df.shape}")
    return df


def build_buyer_features(nifty: pd.DataFrame, vix: pd.DataFrame) -> pd.DataFrame:
    """
    Build feature matrix for buyer engine.
    
    Args:
        nifty: Daily NIFTY OHLCV
        vix: Daily VIX OHLCV
        
    Returns:
        Feature DataFrame
    """
    # Same base as direction
    df = build_direction_features(nifty, vix)
    
    # Range compression
    df["range_10d"] = (df["High"] - df["Low"]).rolling(10).mean()
    df["range_60d"] = (df["High"] - df["Low"]).rolling(60).mean()
    df["range_compression"] = df["range_10d"] / (df["range_60d"] + 1e-6)
    
    # Breakout tendency
    df["closes_above_10d_high"] = (df["Close"] > df["High"].rolling(10).max().shift(1)).astype(int)
    
    logger.info(f"Built buyer features: {df.shape}")
    return df
