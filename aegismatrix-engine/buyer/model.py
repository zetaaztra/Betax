"""
Buyer engine (PulseWave): option buyer analytics.
"""

import numpy as np
import logging
import sys
from pathlib import Path
import joblib

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import MODEL_DIR

logger = logging.getLogger(__name__)


def load_models():
    """
    Load pre-trained buyer models.
    
    Returns:
        Tuple of (breakout_model, spike_model, theta_model)
    """
    try:
        breakout_model = joblib.load(MODEL_DIR / "buyer_breakout.pkl")
        spike_model = joblib.load(MODEL_DIR / "buyer_spike.pkl")
        theta_model = joblib.load(MODEL_DIR / "buyer_theta.pkl")
        return breakout_model, spike_model, theta_model
    except Exception as e:
        logger.error(f"Error loading buyer models: {e}")
        return None, None, None


def compute_breakout_today(features_df, model=None) -> dict:
    """
    Probability of range breakout today.
    
    Args:
        features_df: Feature DataFrame
        model: Trained XGBClassifier
        
    Returns:
        Dict with score, label
    """
    # Handle missing model
    if model is None or features_df is None or len(features_df) == 0:
        # Fallback to heuristic
        if isinstance(features_df, dict):
            range_compression = features_df.get("range_compression", 0.7)
            volatility = features_df.get("volatility", 0.015)
        else:
            range_compression = features_df["range_compression"].iloc[-1] if "range_compression" in features_df.columns else 0.7
            volatility = features_df["volatility"].iloc[-1] if "volatility" in features_df.columns else 0.015
        
        compression_factor = np.clip(1 - range_compression, 0, 1)
        volatility_factor = np.clip(volatility / 0.03, 0, 1)
        score = (compression_factor * 0.6 + volatility_factor * 0.4)
        score = np.clip(score, 0, 1)
        label = "LOW" if score < 0.33 else "MEDIUM" if score < 0.67 else "HIGH"
        return {"score": float(score), "label": label}

    try:
        # Prepare data
        numeric_cols = features_df.select_dtypes(include=[np.number]).columns
        X = features_df[numeric_cols].drop(columns=['label', 'target', 'return'], errors='ignore').values.astype(np.float32)
        last_row = X[-1].reshape(1, -1)
        
        # Predict
        score = float(model.predict_proba(last_row)[0][1])
        label = "LOW" if score < 0.33 else "MEDIUM" if score < 0.67 else "HIGH"
        
        return {"score": score, "label": label}
        
    except Exception as e:
        logger.error(f"Breakout prediction failed: {e}")
        return {"score": 0.5, "label": "MEDIUM"}


def compute_breakout_next(features_df, model=None) -> list[dict]:
    """
    Breakout probability for next 5 days.
    """
    # Get today's base score
    today_res = compute_breakout_today(features_df, model)
    base_score = today_res["score"]
    
    if isinstance(features_df, dict):
        momentum = features_df.get("momentum", 0.0)
    else:
        momentum = features_df["momentum"].iloc[-1] if "momentum" in features_df.columns else 0.0
    
    results = []
    for day in range(1, 6):
        if day <= 2:
            decay = 0.85
            score = base_score * decay + momentum * 0.1
        elif day <= 4:
            decay = 0.60
            score = base_score * decay
        else:
            decay = 0.45
            score = base_score * decay
        
        score = np.clip(score, 0, 1)
        label = "LOW" if score < 0.33 else "MEDIUM" if score < 0.67 else "HIGH"
        
        results.append({
            "day_offset": int(day),
            "score": float(score),
            "label": label
        })
    
    return results


def compute_spike_direction_bias(features_df, model=None) -> dict:
    """
    If spike occurs, probability of UP vs DOWN.
    """
    if model is None or features_df is None or len(features_df) == 0:
        # Fallback
        if isinstance(features_df, dict):
            ret_5d = features_df.get("ret_5d", 0)
        else:
            ret_5d = features_df["ret_5d"].iloc[-1] if "ret_5d" in features_df.columns else 0
        base_prob = 0.5 + ret_5d * 2
        up_prob = np.clip(base_prob, 0.2, 0.8)
        return {"up_prob": float(up_prob), "down_prob": float(1.0 - up_prob)}

    try:
        numeric_cols = features_df.select_dtypes(include=[np.number]).columns
        X = features_df[numeric_cols].drop(columns=['label', 'target', 'return'], errors='ignore').values.astype(np.float32)
        last_row = X[-1].reshape(1, -1)
        
        # Predict UP probability (class 1)
        up_prob = float(model.predict_proba(last_row)[0][1])
        
        return {
            "up_prob": up_prob,
            "down_prob": 1.0 - up_prob
        }
    except Exception as e:
        logger.error(f"Spike direction prediction failed: {e}")
        return {"up_prob": 0.5, "down_prob": 0.5}


def compute_gamma_windows(intraday_df) -> list[dict]:
    """
    Identify high-gamma time windows based on recent intraday volatility patterns.
    
    Args:
        intraday_df: Intraday OHLCV DataFrame (5-minute intervals)
        
    Returns:
        List of dicts with window, score
    """
    if intraday_df is None or intraday_df.empty:
        # Fallback if no data
        return [
            {"window": "09:15-09:45", "score": 45},
            {"window": "14:00-14:30", "score": 35},
            {"window": "15:00-15:30", "score": 55},
        ]
    
    try:
        # Ensure datetime index
        df = intraday_df.copy()
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)

        # Calculate 'Activity' metric: Range * Volume
        # (High - Low) / Open * Volume
        df['range_pct'] = (df['High'] - df['Low']) / df['Open']
        df['activity'] = df['range_pct'] * df['Volume']
        
        # Group by time of day (30-min buckets)
        # We need to handle the time grouping manually since resample works on datetime
        df['time_str'] = df.index.strftime('%H:%M')
        
        # Define 30-min buckets
        buckets = [
            ("09:15", "09:45"), ("09:45", "10:15"), ("10:15", "10:45"),
            ("10:45", "11:15"), ("11:15", "11:45"), ("11:45", "12:15"),
            ("12:15", "12:45"), ("12:45", "13:15"), ("13:15", "13:45"),
            ("13:45", "14:15"), ("14:15", "14:45"), ("14:45", "15:15"),
            ("15:15", "15:30")
        ]
        
        bucket_scores = {}
        
        for start, end in buckets:
            # Filter rows that fall into this bucket
            # This is a simplification; for exact 5-min alignment:
            # 09:15, 09:20, ... 09:40 fall into 09:15-09:45
            
            mask = (df['time_str'] >= start) & (df['time_str'] < end)
            if mask.any():
                avg_score = df.loc[mask, 'activity'].mean()
                bucket_scores[f"{start}-{end}"] = avg_score
            else:
                bucket_scores[f"{start}-{end}"] = 0.0

        # Normalize scores to 0-100 (relative to max activity)
        max_score = max(bucket_scores.values()) if bucket_scores else 1.0
        if max_score == 0: max_score = 1.0
        
        results = []
        for window, raw_score in bucket_scores.items():
            normalized = (raw_score / max_score)
            # Boost score slightly if it's the current time? 
            # For now, just return the historical average intensity
            results.append({
                "window": window,
                "score": float(normalized) # Frontend expects 0-1 (scaled to 100 there) or 0-100?
                # The frontend code we saw earlier multiplied by 100: w.score * 100.
                # So we should return 0-1 float here.
            })
            
        # Sort by score descending and take top 3
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:3]
        
    except Exception as e:
        logger.error(f"Gamma window calculation failed: {e}")
        return [
            {"window": "09:15-09:45", "score": 0.85},
            {"window": "14:00-14:30", "score": 0.75},
            {"window": "15:00-15:30", "score": 0.95},
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
        # Try to get spot from features if available
        if not isinstance(features_df, dict) and "Close" in features_df.columns and len(features_df) > 0:
            spot = float(features_df["Close"].iloc[-1])
        else:
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


def compute_theta_edge_score(features_df, model=None) -> dict:
    """
    Theta vs edge: is premium worth paying?
    """
    if model is None or features_df is None or len(features_df) == 0:
        # Fallback
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
        label = "EDGE_JUSTIFIES_PREMIUM" if score > 0.6 else "BORDERLINE" if score > 0.3 else "DONT_WASTE_PREMIUM"
        return {"score": float(score), "label": label}

    try:
        numeric_cols = features_df.select_dtypes(include=[np.number]).columns
        X = features_df[numeric_cols].drop(columns=['label', 'target', 'return'], errors='ignore').values.astype(np.float32)
        last_row = X[-1].reshape(1, -1)
        
        score = float(model.predict(last_row)[0])
        score = np.clip(score, 0, 1)
        
        if score > 0.6:
            label = "EDGE_JUSTIFIES_PREMIUM"
        elif score > 0.3:
            label = "BORDERLINE"
        else:
            label = "DONT_WASTE_PREMIUM"
            
        return {"score": score, "label": label}
        
    except Exception as e:
        logger.error(f"Theta prediction failed: {e}")
        return {"score": 0.5, "label": "BORDERLINE"}


def infer_buyer_regime(features_df) -> str:
    """
    Infer buyer regime: trending vs mean-revert vs choppy.
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
