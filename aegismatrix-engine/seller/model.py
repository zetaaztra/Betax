"""
Seller engine (RangeShield): option seller analytics.
"""

import numpy as np
import logging
import math
from scipy.stats import norm
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import SELLER_EXPIRY_HORIZON_DAYS, SAFE_RANGE_MULTIPLIER

logger = logging.getLogger(__name__)


def compute_safe_range(spot: float, vol: float, horizon_days: int = SELLER_EXPIRY_HORIZON_DAYS) -> dict:
    """
    Compute statistically conservative safe range band.
    
    Args:
        spot: Current spot price
        vol: Annualized volatility
        horizon_days: Days to expiry horizon
        
    Returns:
        Dict with lower, upper, horizon_days
    """
    T = horizon_days / 252.0
    expected_pct_move = vol * math.sqrt(T)
    move_points = expected_pct_move * spot
    
    k = SAFE_RANGE_MULTIPLIER
    lower = spot - k * move_points
    upper = spot + k * move_points
    
    return {
        "lower": float(lower),
        "upper": float(upper),
        "horizon_days": int(horizon_days)
    }


def compute_max_pain_zone(features_df) -> dict:
    """
    Approximate max pain zone from returns distribution.
    
    Args:
        features_df: Feature DataFrame
        
    Returns:
        Dict with lower, upper, confidence
    """
    close = features_df["Close"].iloc[-1]
    returns = features_df["ret_1d"].dropna()
    
    # Use mode-like approximation
    hist, edges = np.histogram(returns, bins=50)
    mode_idx = np.argmax(hist)
    mode_return = (edges[mode_idx] + edges[mode_idx + 1]) / 2
    
    zone_width = returns.std() * 2
    lower = close * (1 + mode_return - zone_width)
    upper = close * (1 + mode_return + zone_width)
    
    return {
        "lower": float(lower),
        "upper": float(upper),
        "confidence": 0.6
    }


def compute_vol_trap_risk(features_df) -> dict:
    """
    IV vs RV: high IV relative to RV = trap risk.
    
    Args:
        features_df: Feature DataFrame
        
    Returns:
        Dict with score, label, iv_percentile, rv_percentile
    """
    if features_df is None or len(features_df) == 0:
        logger.warning("Empty features_df, returning default trap risk")
        return {
            "score": 0.5,
            "label": "MEDIUM",
            "iv_percentile": 0.5,
            "rv_percentile": 0.5
        }
    
    # IV proxy = last VIX level
    iv_level = features_df["Close_vix"].iloc[-1] if "Close_vix" in features_df.columns else 15
    rv_level = features_df["vol_20d"].iloc[-1] * 100 if "vol_20d" in features_df.columns else 15
    
    # Percentiles
    iv_series = features_df["Close_vix"].tail(252) if "Close_vix" in features_df.columns else pd.Series([15] * 252)
    rv_series = (features_df["vol_20d"].tail(252) * 100) if "vol_20d" in features_df.columns else pd.Series([15] * 252)
    
    iv_pct = (iv_level >= iv_series.values).sum() / len(iv_series)
    rv_pct = (rv_level >= rv_series.values).sum() / len(rv_series)
    
    trap_raw = iv_pct - rv_pct
    score = np.clip(trap_raw / 2 + 0.5, 0, 1)
    
    label = "LOW" if score < 0.33 else "MEDIUM" if score < 0.67 else "HIGH"
    
    return {
        "score": float(score),
        "label": label,
        "iv_percentile": float(iv_pct),
        "rv_percentile": float(rv_pct)
    }


def compute_skew_pressure(features_df) -> dict:
    """
    Asymmetry of returns: downside vs upside.
    
    Args:
        features_df: Feature DataFrame
        
    Returns:
        Dict with put_skew, call_skew, net_skew
    """
    returns = features_df["ret_1d"].tail(60).dropna()
    
    downside_tail = returns[returns < 0].mean() if (returns < 0).any() else 0
    upside_tail = returns[returns > 0].mean() if (returns > 0).any() else 0
    
    put_skew_raw = (abs(downside_tail) - abs(upside_tail)) / (abs(upside_tail) + 1e-6)
    call_skew_raw = (abs(upside_tail) - abs(downside_tail)) / (abs(downside_tail) + 1e-6)
    
    put_skew = np.clip(put_skew_raw / 2, -1, 1)
    call_skew = np.clip(call_skew_raw / 2, -1, 1)
    net_skew = put_skew - call_skew
    
    return {
        "put_skew": float(put_skew),
        "call_skew": float(call_skew),
        "net_skew": float(net_skew)
    }


def compute_expiry_stress(features_df) -> dict:
    """
    Stress score based on vol regime, trap, and time.
    
    Args:
        features_df: Feature DataFrame
        
    Returns:
        Dict with score, label
    """
    vol = features_df["vol_20d"].iloc[-1] if "vol_20d" in features_df.columns else 0.01
    trap_score = compute_vol_trap_risk(features_df)["score"]
    
    # Normalize vol
    normalized_vol = min(1.0, vol / 0.03)
    
    # Expiry stress composite
    stress = 0.6 * trap_score + 0.4 * normalized_vol
    stress = np.clip(stress, 0, 1)
    
    label = "CALM" if stress < 0.33 else "CAUTION" if stress < 0.67 else "HOSTILE"
    
    return {
        "score": float(stress),
        "label": label
    }


def compute_breach_probability_curve(spot: float, vol: float, horizon_days: int = 30) -> list[dict]:
    """
    Probability of breaching various distance levels.
    
    Args:
        spot: Current spot
        vol: Annualized volatility
        horizon_days: Horizon
        
    Returns:
        List of {"distance": int, "probability": float}
    """
    T = horizon_days / 252.0
    sigma_T = vol * math.sqrt(T)
    
    distances = [100, 200, 300, 400]
    results = []
    
    for dist in distances:
        dist_pct = dist / spot
        z = dist_pct / (sigma_T + 1e-6)
        prob = 2 * (1 - norm.cdf(z))
        prob = np.clip(prob, 0, 1)
        
        results.append({
            "distance": int(dist),
            "probability": float(prob)
        })
    
    return results


def compute_seller_flag(trap_score: dict, expiry_stress: dict) -> dict:
    """
    Derive seller flag from sub-components.
    
    Args:
        trap_score: From compute_vol_trap_risk
        expiry_stress: From compute_expiry_stress
        
    Returns:
        Dict with label, color, reasons
    """
    reasons = []
    
    if trap_score["label"] == "HIGH":
        reasons.append("HIGH_TRAP")
    if expiry_stress["label"] == "HOSTILE":
        reasons.append("ELEVATED_STRESS")
    
    if not reasons:
        label, color = "FAVOURABLE", "GREEN"
    elif "ELEVATED_STRESS" in reasons:
        label, color = "CAUTION", "AMBER"
    else:
        label, color = "CAUTION", "AMBER"
    
    return {
        "label": label,
        "color": color,
        "reasons": reasons
    }


import pandas as pd
