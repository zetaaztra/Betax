"""
Buyer engine (PulseWave): option buyer analytics.
"""

import numpy as np
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)


def compute_breakout_today(features_df) -> dict:
    """
    Probability of range breakout today.
    
    Args:
        features_df: Feature DataFrame
        
    Returns:
        Dict with score, label
    """
    # Heuristic based on range compression and recent trend
    if isinstance(features_df, dict):
        range_compression = features_df.get("range_compression", 0.7)
        volatility = features_df.get("volatility", 0.015)
    else:
        range_compression = features_df["range_compression"].iloc[-1] if "range_compression" in features_df.columns else 0.7
        volatility = features_df["volatility"].iloc[-1] if "volatility" in features_df.columns else 0.015
    
    # More compression + higher volatility = more likely to breakout
    # Range compression close to 0 = tight range = breakout signal
    compression_factor = np.clip(1 - range_compression, 0, 1)  # 0-1 score
    volatility_factor = np.clip(volatility / 0.03, 0, 1)  # normalize by 3% daily vol
    
    # Weighted combination
    score = (compression_factor * 0.6 + volatility_factor * 0.4)
    score = np.clip(score, 0, 1)
    
    label = "LOW" if score < 0.33 else "MEDIUM" if score < 0.67 else "HIGH"
    
    return {
        "score": float(score),
        "label": label
    }


def compute_breakout_next(features_df) -> list[dict]:
    """
    Breakout probability for next 5 days.
    
    Args:
        features_df: Feature DataFrame
        
    Returns:
        List of dicts with day_offset, score, label
    """
    base_score = compute_breakout_today(features_df)["score"]
    
    # Extract momentum for trend continuation probability
    if isinstance(features_df, dict):
        momentum = features_df.get("momentum", 0.0)
    else:
        momentum = features_df["momentum"].iloc[-1] if "momentum" in features_df.columns else 0.0
    
    results = []
    for day in range(1, 6):
        # Different days have different breakout probabilities
        # Day 1-2: higher probability (momentum continues)
        # Day 3-4: lower probability (mean reversion)
        # Day 5: potential reversal
        
        if day <= 2:
            # Early days: momentum-driven
            decay = 0.85 + np.random.randn() * 0.05
            score = base_score * decay + momentum * 0.1
        elif day <= 4:
            # Mid days: mean reversion sets in
            decay = 0.60 + np.random.randn() * 0.08
            score = base_score * decay
        else:
            # Day 5: potential reversal
            decay = 0.45 + np.random.randn() * 0.1
            score = base_score * decay
        
        score = np.clip(score, 0, 1)  # Keep in 0-1 range for schema
        
        label = "LOW" if score < 0.33 else "MEDIUM" if score < 0.67 else "HIGH"
        
        results.append({
            "day_offset": int(day),
            "score": float(score),  # Return as 0-1 for schema validation
            "label": label
        })
    
    return results


def compute_spike_direction_bias(features_df) -> dict:
    """
    If spike occurs, probability of UP vs DOWN.
    
    Args:
        features_df: Feature DataFrame
        
    Returns:
        Dict with up_prob, down_prob
    """
    # Simple heuristic: recent trend bias
    if isinstance(features_df, dict):
        ret_5d = features_df.get("ret_5d", 0)
    else:
        ret_5d = features_df["ret_5d"].iloc[-1] if "ret_5d" in features_df.columns else 0
    
    base_prob = 0.5 + ret_5d * 2  # scale returns to affect probability
    up_prob = np.clip(base_prob, 0.2, 0.8)
    down_prob = 1.0 - up_prob
    
    return {
        "up_prob": float(up_prob),
        "down_prob": float(down_prob)
    }


def compute_gamma_windows(intraday_df) -> list[dict]:
    """
    Time windows with highest gamma exposure (for gamma scalping).
    
    Args:
        intraday_df: Intraday OHLCV DataFrame
        
    Returns:
        List of dicts with time_block, score
    """
    if intraday_df.empty:
        return []
    
    # Typical high-gamma times during Indian market hours
    return [
        {"time_block": "09:15-09:45", "score": 45},  # Opening volatility
        {"time_block": "14:00-14:30", "score": 35},  # Intraday continuation
        {"time_block": "15:00-15:30", "score": 55},  # Near close
    ]


def compute_breakout_levels(features_df, nifty_df) -> dict:
    """
    Upper and lower breakout reference levels.
    Based on recent volatility bands.
    
    Args:
        features_df: Feature DataFrame
        nifty_df: Daily NIFTY data for current spot
        
    Returns:
        Dict with upper, lower levels
    """
    if isinstance(nifty_df, dict) or len(nifty_df) == 0:
        spot = 26000
    else:
        spot = float(nifty_df["Close"].iloc[-1])
    
    # Use recent volatility to define levels
    if isinstance(features_df, dict):
        vol_20d = features_df.get("vol_20d", 0.01)
    else:
        vol_20d = features_df["vol_20d"].iloc[-1] if "vol_20d" in features_df.columns and len(features_df) > 0 else 0.01
    
    # Levels are spot +/- 1.5x recent volatility
    level_distance = spot * vol_20d * 1.5
    
    return {
        "upper": float(spot + level_distance),
        "lower": float(spot - level_distance)
    }


def compute_gamma_windows(intraday_df) -> list[dict]:
    """
    Intraday windows with high gamma potential.
    
    Args:
        intraday_df: Intraday DataFrame
        
    Returns:
        List of {"window": "HH:MM-HH:MM", "score": 0-1}
    """
    # Already computed in features/intraday_features.py
    # This is a stub in case we need additional processing
    
    intraday_df = intraday_df.copy()
    intraday_df["ret"] = intraday_df["Close"].pct_change()
    session_vol = intraday_df["ret"].std()
    
    windows = [
        {"window": "09:45-10:15", "score": 0.82},
        {"window": "10:15-10:45", "score": 0.40},
        {"window": "14:30-15:15", "score": 0.76},
    ]
    
    # Add some randomness
    for w in windows:
        w["score"] += np.random.randn() * 0.05
        w["score"] = float(np.clip(w["score"], 0, 1))
    
    return windows


def compute_theta_edge_score(features_df) -> dict:
    """
    Theta vs edge: is premium worth paying?
    
    Args:
        features_df: Feature DataFrame
        
    Returns:
        Dict with score, label
    """
    # Rough heuristic: vol / vix proxy
    if isinstance(features_df, dict):
        vol = features_df.get("vol_20d", 0.01)
        vix = features_df.get("vix", 15)
    else:
        vol = features_df["vol_20d"].iloc[-1] if "vol_20d" in features_df.columns else 0.01
        vix = features_df["Close_vix"].iloc[-1] if "Close_vix" in features_df.columns else 15
    
    forecast_vol = vol * 100
    implied_vol_proxy = vix
    
    ratio = forecast_vol / (implied_vol_proxy + 1e-6)
    score = np.clip(ratio / 2, 0, 1)
    
    if score > 0.6:
        label = "EDGE_JUSTIFIES_PREMIUM"
    elif score > 0.3:
        label = "BORDERLINE"
    else:
        label = "DONT_WASTE_PREMIUM"
    
    return {
        "score": float(score),
        "label": label
    }


def infer_buyer_regime(features_df) -> str:
    """
    Infer buyer regime: trending vs mean-revert vs choppy.
    
    Args:
        features_df: Feature DataFrame
        
    Returns:
        Regime label
    """
    if isinstance(features_df, dict):
        ret_5d = features_df.get("ret_5d", 0)
        vol = features_df.get("vol_20d", 0.01)
    else:
        ret_5d = features_df["ret_5d"].iloc[-1] if "ret_5d" in features_df.columns else 0
        vol = features_df["vol_20d"].iloc[-1] if "vol_20d" in features_df.columns else 0.01
    
    if abs(ret_5d) > 0.02 and vol < 0.02:
        regime = "TREND_FOLLOWING"
    elif vol > 0.025:
        regime = "CHOPPY"
    else:
        regime = "MEAN_REVERT"
    
    return regime


def compute_buyer_environment(breakout_today: dict, theta_edge: dict, regime: str) -> dict:
    """
    Derive buyer environment flag.
    
    Args:
        breakout_today: From compute_breakout_today
        theta_edge: From compute_theta_edge_score
        regime: From infer_buyer_regime
        
    Returns:
        Dict with label, color, reasons
    """
    reasons = []
    
    if breakout_today["label"] == "HIGH":
        reasons.append("HIGH_BREAKOUT_SCORE")
    if theta_edge["label"] == "EDGE_JUSTIFIES_PREMIUM":
        reasons.append("THETA_EDGE_FAVOURABLE")
    if regime == "TREND_FOLLOWING":
        reasons.append("TREND_FOLLOWING")
    
    if "HIGH_BREAKOUT_SCORE" in reasons and "THETA_EDGE_FAVOURABLE" in reasons:
        label, color = "PREMIUM_FRIENDLY", "GREEN"
    elif "HIGH_BREAKOUT_SCORE" in reasons:
        label, color = "SPECULATIVE_ONLY", "AMBER"
    else:
        label, color = "UNFAVOURABLE", "RED"
    
    return {
        "label": label,
        "color": color,
        "reasons": reasons
    }
