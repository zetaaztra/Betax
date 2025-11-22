"""
Today direction: combines daily bias + intraday context.
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


def compute_today_direction(daily_bias: dict, intraday_feats: dict) -> dict:
    """
    Combine daily model bias with intraday features to compute today's direction.
    
    Args:
        daily_bias: From direction model for T+1
        intraday_feats: From build_today_direction_features
        
    Returns:
        Dict with direction, expected_move_points, conviction, etc.
    """
    
    # Weighted combination
    w1, w2, w3, w4 = 0.6, 0.25, 0.1, 0.05
    
    daily_bias_logit = daily_bias.get("logit", 0)  # range approx -2 to +2
    gap_pct = intraday_feats.get("gap_pct", 0)
    orb_score = intraday_feats.get("orb_breakout_score", 0)
    intraday_vol = intraday_feats.get("realized_vol_norm", 0)
    
    score = (
        w1 * daily_bias_logit +
        w2 * (gap_pct * 100) +  # scale to -2..2 range
        w3 * (orb_score - 0.5) * 2 +
        w4 * (intraday_vol - 0.5) * 2
    )
    
    # Thresholds
    theta_up = 0.3
    theta_down = -0.3
    
    if score > theta_up:
        direction = "UP"
    elif score < theta_down:
        direction = "DOWN"
    else:
        direction = "NEUTRAL"
    
    # Conviction
    max_score = 2.0
    conviction = min(1.0, abs(score) / max_score)
    
    # Expected move
    daily_expected_move = daily_bias.get("expected_move_points_today", 50)
    intraday_multiplier = 0.6  # intraday moves tend to be smaller
    expected_move_points = daily_expected_move * intraday_multiplier
    
    return {
        "direction": direction,
        "expected_move_points": float(expected_move_points),
        "conviction": float(conviction),
        "intraday_volatility_score": float(intraday_feats.get("realized_vol_norm", 0)),
    }
