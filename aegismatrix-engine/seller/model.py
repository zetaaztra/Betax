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

import joblib

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import SELLER_EXPIRY_HORIZON_DAYS, SAFE_RANGE_MULTIPLIER, MODEL_DIR

logger = logging.getLogger(__name__)


def load_models():
    """
    Load pre-trained seller models.
    
    Returns:
        Tuple of (trap_model, regime_model, breach_model)
    """
    try:
        trap_model = joblib.load(MODEL_DIR / "seller_trap.pkl")
        regime_model = joblib.load(MODEL_DIR / "seller_regime.pkl")
        breach_model = joblib.load(MODEL_DIR / "seller_breach.pkl")
        return trap_model, regime_model, breach_model
    except Exception as e:
        logger.error(f"Error loading seller models: {e}")
        return None, None, None


def compute_safe_range(spot: float, vol: float, horizon_days: int = SELLER_EXPIRY_HORIZON_DAYS) -> dict:
    """
    Compute statistically conservative safe range band.
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
    """
    close = features_df["Close"].iloc[-1]
    returns = features_df["ret_1d"].dropna()
    
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


def compute_vol_trap_risk(features_df, model=None) -> dict:
    """
    IV vs RV: high IV relative to RV = trap risk.
    """
    if features_df is None or len(features_df) == 0:
        return {"score": 0.5, "label": "MEDIUM", "iv_percentile": 0.5, "rv_percentile": 0.5}
    
    # Calculate percentiles for display regardless of model
    iv_level = features_df["Close_vix"].iloc[-1] if "Close_vix" in features_df.columns else 15
    rv_level = features_df["vol_20d"].iloc[-1] * 100 if "vol_20d" in features_df.columns else 15
    iv_series = features_df["Close_vix"].tail(252) if "Close_vix" in features_df.columns else pd.Series([15] * 252)
    rv_series = (features_df["vol_20d"].tail(252) * 100) if "vol_20d" in features_df.columns else pd.Series([15] * 252)
    iv_pct = (iv_level >= iv_series.values).sum() / len(iv_series)
    rv_pct = (rv_level >= rv_series.values).sum() / len(rv_series)

    if model is None:
        # Fallback heuristic
        trap_raw = iv_pct - rv_pct
        score = np.clip(trap_raw / 2 + 0.5, 0, 1)
        label = "LOW" if score < 0.33 else "MEDIUM" if score < 0.67 else "HIGH"
        return {"score": float(score), "label": label, "iv_percentile": float(iv_pct), "rv_percentile": float(rv_pct)}

    try:
        numeric_cols = features_df.select_dtypes(include=[np.number]).columns
        X = features_df[numeric_cols].drop(columns=['label', 'target', 'return'], errors='ignore').values.astype(np.float32)
        last_row = X[-1].reshape(1, -1)
        
        # Predict trap probability (class 1)
        score = float(model.predict_proba(last_row)[0][1])
        label = "LOW" if score < 0.33 else "MEDIUM" if score < 0.67 else "HIGH"
        
        return {
            "score": score,
            "label": label,
            "iv_percentile": float(iv_pct),
            "rv_percentile": float(rv_pct)
        }
    except Exception as e:
        logger.error(f"Trap prediction failed: {e}")
        return {"score": 0.5, "label": "MEDIUM", "iv_percentile": 0.5, "rv_percentile": 0.5}


def compute_skew_pressure(features_df) -> dict:
    """
    Asymmetry of returns: downside vs upside.
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


def compute_expiry_stress(features_df, model=None) -> dict:
    """
    Stress score based on vol regime, trap, and time.
    """
    if features_df is None or len(features_df) == 0:
        return {"score": 0.5, "label": "CAUTION"}
        
    if model is None:
        # Fallback
        vol = features_df["vol_20d"].iloc[-1] if "vol_20d" in features_df.columns else 0.01
        trap_score = compute_vol_trap_risk(features_df)["score"]
        normalized_vol = min(1.0, vol / 0.03)
        stress = 0.6 * trap_score + 0.4 * normalized_vol
        stress = np.clip(stress, 0, 1)
        label = "CALM" if stress < 0.33 else "CAUTION" if stress < 0.67 else "HOSTILE"
        return {"score": float(stress), "label": label}

    try:
        # We use the regime model as a proxy for stress? 
        # Or did we train a stress model?
        # train_seller.py trains: trap, regime, breach.
        # It does NOT train a 'stress' model.
        # So we should use the Regime model to inform stress.
        
        numeric_cols = features_df.select_dtypes(include=[np.number]).columns
        X = features_df[numeric_cols].drop(columns=['label', 'target', 'return'], errors='ignore').values.astype(np.float32)
        last_row = X[-1].reshape(1, -1)
        
        # Predict Regime: 0=Low, 1=Med, 2=High
        regime_probs = model.predict_proba(last_row)[0]
        # Weighted stress score: 0*p0 + 0.5*p1 + 1.0*p2
        stress = 0.0 * regime_probs[0] + 0.5 * regime_probs[1] + 1.0 * regime_probs[2]
        
        label = "CALM" if stress < 0.33 else "CAUTION" if stress < 0.67 else "HOSTILE"
        return {"score": float(stress), "label": label}
        
    except Exception as e:
        logger.error(f"Stress/Regime prediction failed: {e}")
        return {"score": 0.5, "label": "CAUTION"}


def compute_breach_probability_curve(spot: float, vol: float, horizon_days: int = 30, model=None, features_df=None) -> list[dict]:
    """
    Probability of breaching various distance levels.
    """
    # If no model, use theoretical
    if model is None or features_df is None:
        T = horizon_days / 252.0
        sigma_T = vol * math.sqrt(T)
        # Use percentages of spot for dynamic distances
        pct_distances = [0.005, 0.01, 0.015, 0.02] # 0.5%, 1%, 1.5%, 2%
        distances = [int(spot * p) for p in pct_distances]
        
        results = []
        for dist in distances:
            dist_pct = dist / spot
            z = dist_pct / (sigma_T + 1e-6)
            prob = 2 * (1 - norm.cdf(z))
            prob = np.clip(prob, 0, 1)
            results.append({"distance": int(dist), "probability": float(prob)})
        return results

    try:
        # The model predicts binary breach of a specific range (SAFE_RANGE_MULTIPLIER).
        # It doesn't predict curve directly.
        # But we can use the probability of breach as a base scaler for the theoretical curve.
        
        numeric_cols = features_df.select_dtypes(include=[np.number]).columns
        X = features_df[numeric_cols].drop(columns=['label', 'target', 'return'], errors='ignore').values.astype(np.float32)
        last_row = X[-1].reshape(1, -1)
        
        model_prob = float(model.predict_proba(last_row)[0][1])
        
        # Adjust theoretical curve using model probability
        # If model says high prob, we shift curve up.
        
        T = horizon_days / 252.0
        sigma_T = vol * math.sqrt(T)
        distances = [100, 200, 300, 400]
        results = []
        
        # Theoretical base prob for the trained range (1.5 std dev)
        # 1.5 sigma breach prob is approx 13% (2-sided)
        theoretical_base = 2 * (1 - norm.cdf(1.5))
        
        # Adjustment factor
        adj_factor = model_prob / (theoretical_base + 1e-6)
        adj_factor = np.clip(adj_factor, 0.5, 2.0) # Limit adjustment
        
        # Use percentages of spot for dynamic distances
        pct_distances = [0.005, 0.01, 0.015, 0.02] # 0.5%, 1%, 1.5%, 2%
        distances = [int(spot * p) for p in pct_distances]
        
        for dist in distances:
            dist_pct = dist / spot
            z = dist_pct / (sigma_T + 1e-6)
            prob = 2 * (1 - norm.cdf(z))
            prob = prob * adj_factor
            prob = np.clip(prob, 0, 1)
            results.append({"distance": int(dist), "probability": float(prob)})
            
        return results
        
    except Exception as e:
        logger.error(f"Breach curve prediction failed: {e}")
        return []


def compute_seller_flag(trap_score: dict, expiry_stress: dict) -> dict:
    """
    Derive seller flag from sub-components.
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
