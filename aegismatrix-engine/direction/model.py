"""
Direction engine model predictions.
Handles horizon-based directional forecasts.
"""

import numpy as np
import logging
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import MODEL_DIR, DIRECTION_HORIZONS

logger = logging.getLogger(__name__)


def load_models():
    """
    Load pre-trained direction models.
    
    Returns:
        Tuple of (direction_model, magnitude_model)
    """
    # Placeholder: actual models would be joblib/torch loaded
    logger.warning("Using placeholder models - replace with actual trained models")
    return None, None


def predict_direction_horizons(features_df, horizons=DIRECTION_HORIZONS) -> dict:
    """
    Predict direction and magnitude for each horizon.
    
    Args:
        features_df: Feature DataFrame from daily_features
        horizons: List of horizon days
        
    Returns:
        Dict keyed by horizon string (t1, t3, etc)
    """
    results = {}
    
    # Handle empty dataframe
    if features_df is None or len(features_df) == 0:
        logger.warning("Empty features_df provided, generating placeholder predictions")
        for h in horizons:
            results[f"t{h}"] = {
                "direction": "NEUTRAL",
                "expected_move_points": 50.0,
                "conviction": 0.5
            }
        return results
    
    # Placeholder: real implementation would use trained models
    # For now, simple heuristic based on features
    
    last_row = features_df.iloc[-1]
    rsi = last_row.get("rsi_14", 50)
    ret_5d = last_row.get("ret_5d", 0)
    vol_20d = last_row.get("vol_20d", 0.01)
    
    for h in horizons:
        # Placeholder logic
        score = (rsi - 50) / 50 + ret_5d * 10 + np.random.randn() * 0.1
        
        if score > 0.2:
            direction = "UP"
            conviction = min(0.95, abs(score) / 2)
        elif score < -0.2:
            direction = "DOWN"
            conviction = min(0.95, abs(score) / 2)
        else:
            direction = "NEUTRAL"
            conviction = 0.5
        
        expected_move = (vol_20d * np.sqrt(h / 252)) * last_row.get("Close", 20000) * 100  # rough point estimate
        
        results[f"t{h}"] = {
            "direction": direction,
            "expected_move_points": float(expected_move),
            "conviction": float(conviction)
        }
    
    logger.info(f"Generated direction predictions for {len(horizons)} horizons")
    return results


def predict_direction_risk_score(features_df) -> float:
    """
    Compute directional risk score (0-1).
    Higher = more uncertain.
    
    Args:
        features_df: Feature DataFrame
        
    Returns:
        Risk score 0-1
    """
    if features_df is None or len(features_df) == 0:
        logger.warning("Empty features_df, returning default risk score")
        return 0.5
    
    last_row = features_df.iloc[-1]
    
    # Simple heuristic
    vol = last_row.get("vol_20d", 0.01)
    normalized_vol = min(1.0, vol / 0.03)  # normalize to 0.03 as "high" vol
    
    risk_score = normalized_vol * 0.7 + np.random.randn() * 0.1
    risk_score = np.clip(risk_score, 0, 1)
    
    return float(risk_score)


def infer_regime(nifty_df, vix_df) -> str:
    """
    Infer current market regime.
    
    Args:
        nifty_df: NIFTY daily data
        vix_df: VIX daily data
        
    Returns:
        Regime label
    """
    last_nifty_row = nifty_df.iloc[-1]
    last_vix_row = vix_df.iloc[-1]
    
    recent_return = nifty_df["Close"].pct_change().tail(5).mean()
    vix_level = last_vix_row["Close"]
    
    if vix_level < 15 and recent_return > 0:
        regime = "LOW_VOL_BULL"
    elif vix_level > 25 and recent_return < 0:
        regime = "HIGH_VOL_BEAR"
    elif vix_level > 20 or abs(recent_return) < 0.001:
        regime = "SIDEWAYS_CHOP"
    else:
        regime = "TREND_FOLLOWING"
    
    return regime
