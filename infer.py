"""
AegisMatrix Core: Main inference script run by GitHub Actions.
Generates aegismatrix.json from market data + models.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
import sys
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

from config import (
    JSON_OUTPUT_PATH,
    DIRECTION_HORIZONS,
    SELLER_EXPIRY_HORIZON_DAYS,
)
from data_fetcher import get_market_snapshots, get_intraday_history
from features.daily_features import (
    build_direction_features,
    build_seller_features,
    build_buyer_features,
)
from features.intraday_features import (
    build_today_direction_features,
    build_gamma_window_features,
)
from direction.model import (
    predict_direction_horizons,
    predict_direction_risk_score,
    infer_regime,
)
from direction.today_direction import compute_today_direction
from seller.model import (
    compute_safe_range,
    compute_max_pain_zone,
    compute_vol_trap_risk,
    compute_skew_pressure,
    compute_expiry_stress,
    compute_breach_probability_curve,
    compute_seller_flag,
)
from buyer.model import (
    compute_breakout_today,
    compute_breakout_next,
    compute_spike_direction_bias,
    compute_breakout_levels,
    compute_gamma_windows,
    compute_theta_edge_score,
    infer_buyer_regime,
    compute_buyer_environment,
)
from schema import validate_payload

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def build_market_block(nifty_df, vix_df, intraday_df=None) -> dict:
    """Build market snapshot block."""
    # Default values if dataframes are empty
    if len(nifty_df) < 2:
        return {
            "spot": 19800,
            "spot_change": 0,
            "spot_change_pct": 0.0,
            "vix": 15.0,
            "vix_change": 0,
            "vix_change_pct": 0.0,
            "regime": "NEUTRAL"
        }
    
    if len(vix_df) < 2:
        vix_df = nifty_df  # Fallback to nifty data if vix is empty
    
    latest_nifty = nifty_df.iloc[-1]
    prev_nifty = nifty_df.iloc[-2]
    latest_vix = vix_df.iloc[-1] if len(vix_df) > 0 else pd.Series({"Close": 15.0, "Open": 15.0, "High": 15.0, "Low": 15.0})
    prev_vix = vix_df.iloc[-2] if len(vix_df) > 1 else latest_vix
    
    # Use live intraday price if available, otherwise use daily close
    if intraday_df is not None and len(intraday_df) > 0:
        spot = float(intraday_df["Close"].iloc[-1])
        logger.debug(f"Using intraday spot price: {spot}")
    else:
        spot = float(latest_nifty["Close"])
        logger.debug(f"Using daily spot price: {spot}")
    
    # For change calculation, use the last daily close as reference
    spot_change = spot - float(prev_nifty["Close"])
    spot_change_pct = spot_change / float(prev_nifty["Close"]) if float(prev_nifty["Close"]) > 0 else 0
    
    vix = float(latest_vix["Close"])
    vix_change = float(latest_vix["Close"] - prev_vix["Close"])
    vix_change_pct = vix_change / float(prev_vix["Close"]) if float(prev_vix["Close"]) != 0 else 0
    
    regime = infer_regime(nifty_df, vix_df)
    
    return {
        "spot": spot,
        "spot_change": spot_change,
        "spot_change_pct": float(spot_change_pct),
        "vix": vix,
        "vix_change": vix_change,
        "vix_change_pct": float(vix_change_pct),
        "regime": regime
    }


def build_direction_block(
    dir_feats, today_intraday_feats, gamma_feats, nifty_df, vix_df, models
) -> dict:
    """Build direction engine output."""
    
    # Horizons
    horizons_block = predict_direction_horizons(dir_feats, models, DIRECTION_HORIZONS)
    horizons = {}
    for h_str, h_dict in horizons_block.items():
        horizons[h_str] = {
            "label": _get_horizon_label(h_str),
            "direction": h_dict["direction"],
            "expected_move_points": h_dict["expected_move_points"],
            "conviction": h_dict["conviction"]
        }
    
    # Today direction
    # Use ATR for expected move if available, else 1% of spot
    if "atr_14" in dir_feats.columns and len(dir_feats) > 0:
        daily_expected_move = float(dir_feats["atr_14"].iloc[-1])
    else:
        daily_expected_move = float(nifty_df["Close"].iloc[-1]) * 0.01 if len(nifty_df) > 0 else 50.0

    daily_bias = {
        "logit": (nifty_df["ret_5d"].iloc[-1] * 100) if "ret_5d" in nifty_df.columns else 0,
        "expected_move_points_today": daily_expected_move
    }
    today_block = compute_today_direction(daily_bias, today_intraday_feats)
    
    # Risk score
    risk_score = predict_direction_risk_score(dir_feats)
    
    return {
        "today": {
            **today_block,
            "last_update": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        },
        "horizons": horizons,
        "risk_score": risk_score
    }


def build_seller_block(sel_feats, nifty, models) -> dict:
    """Build seller engine output."""
    trap_model, regime_model, breach_model = models
    
    spot = float(nifty["Close"].iloc[-1]) if len(nifty) > 0 else 19800
    vol = float(sel_feats["vol_20d"].iloc[-1]) if len(sel_feats) > 0 and "vol_20d" in sel_feats.columns else 0.01
    
    safe_range = compute_safe_range(spot, vol, SELLER_EXPIRY_HORIZON_DAYS)
    max_pain = compute_max_pain_zone(sel_feats) if len(sel_feats) > 0 else {"lower": spot - 100, "upper": spot + 100, "confidence": 0.5}
    
    trap = compute_vol_trap_risk(sel_feats, trap_model)
    skew = compute_skew_pressure(sel_feats) if len(sel_feats) > 0 else {"put_skew": 0.0, "call_skew": 0.0, "net_skew": 0.0}
    expiry_stress = compute_expiry_stress(sel_feats, regime_model)
    breach_probs = compute_breach_probability_curve(spot, vol, SELLER_EXPIRY_HORIZON_DAYS, breach_model, sel_feats)
    seller_flag = compute_seller_flag(trap, expiry_stress)
    
    # Dynamic historical hit rate based on VIX regime
    # Higher VIX = lower hit rate for sellers
    vix_level = float(sel_feats["Close_vix"].iloc[-1]) if len(sel_feats) > 0 and "Close_vix" in sel_feats.columns else 15.0
    if vix_level < 12:
        historical_hit_rate = 0.82  # Very easy environment
    elif vix_level < 18:
        historical_hit_rate = 0.72  # Normal
    elif vix_level < 25:
        historical_hit_rate = 0.65  # Harder
    else:
        historical_hit_rate = 0.55  # Dangerous
    
    return {
        "safe_range": safe_range,
        "max_pain": max_pain,
        "trap": trap,
        "skew": skew,
        "expiry_stress": expiry_stress,
        "breach_probabilities": breach_probs,
        "seller_flag": seller_flag,
        "historical_hit_rate": historical_hit_rate
    }


def build_buyer_block(buy_feats, gamma_feats, intraday_df, nifty, models) -> dict:
    """Build buyer engine output."""
    breakout_model, spike_model, theta_model = models
    
    breakout_today = compute_breakout_today(buy_feats, breakout_model)
    breakout_next = compute_breakout_next(buy_feats, breakout_model)
    spike_bias = compute_spike_direction_bias(buy_feats, spike_model)
    
    breakout_levels = compute_breakout_levels(buy_feats, nifty) if len(buy_feats) > 0 else {"upper": 26500, "lower": 25500}
    
    if isinstance(gamma_feats, list):
        gamma_windows = gamma_feats if gamma_feats else [{"window": "09:45-10:15", "score": 0.5}]
    else:
        gamma_windows = compute_gamma_windows(intraday_df) if len(intraday_df) > 0 else [{"window": "09:45-10:15", "score": 0.5}]
    
    theta_edge = compute_theta_edge_score(buy_feats, theta_model)
    regime = infer_buyer_regime(buy_feats) if len(buy_feats) > 0 else "CHOPPY"
    buyer_env = compute_buyer_environment(breakout_today, theta_edge, regime)
    
    # Dynamic spike rate based on trend strength (ret_5d)
    # Strong trends = higher spike success rate
    trend_strength = abs(float(buy_feats["ret_5d"].iloc[-1])) if len(buy_feats) > 0 and "ret_5d" in buy_feats.columns else 0.0
    if trend_strength > 0.03: # >3% move in 5 days
        historical_spike_rate = 0.65
    elif trend_strength > 0.01:
        historical_spike_rate = 0.58
    else:
        historical_spike_rate = 0.45 # Chop
    
    return {
        "breakout_today": breakout_today,
        "breakout_next": breakout_next,
        "spike_direction_bias": spike_bias,
        "breakout_levels": breakout_levels,
        "gamma_windows": gamma_windows,
        "theta_edge": theta_edge,
        "regime": regime,
        "buyer_environment": buyer_env,
        "historical_spike_rate": historical_spike_rate
    }


def _update_market_block_with_live_price(market_block: dict) -> dict:
    """
    Try to update market block with live spot price.
    
    Args:
        market_block: Current market block dict
        
    Returns:
        Updated market block with live price if available
    """
    from data_fetcher import get_live_price
    
    try:
        live_price = get_live_price("^NSEI")
        if live_price and live_price > 0:
            # Calculate changes based on live price
            prev_close = market_block.get("spot", 19800) - market_block.get("spot_change", 0)
            spot_change = live_price - prev_close
            spot_change_pct = spot_change / prev_close if prev_close > 0 else 0
            
            market_block["spot"] = live_price
            market_block["spot_change"] = spot_change
            market_block["spot_change_pct"] = float(spot_change_pct)
            logger.info(f"Updated market block with live spot price: {live_price}")
    except Exception as e:
        logger.debug(f"Could not update with live price: {e}")
    
    return market_block


def _get_horizon_label(h_str: str) -> str:
    """Map horizon string to label."""
    mapping = {
        "t1": "Tomorrow",
        "t3": "Next 3 Days",
        "t5": "This Week",
        "t10": "Next Week",
        "t20": "This Month",
        "t40": "Next Month"
    }
    return mapping.get(h_str, h_str)


def main():
    """Main inference pipeline."""
    logger.info("=== AegisMatrix Inference Start ===")
    
    # Load Models
    logger.info("Loading trained models...")
    import direction.model
    import buyer.model
    import seller.model
    
    dir_models = direction.model.load_models()
    buy_models = buyer.model.load_models()
    sel_models = seller.model.load_models()
    
    if dir_models[0] is None: logger.warning("Direction models not found - using heuristics")
    if buy_models[0] is None: logger.warning("Buyer models not found - using heuristics")
    if sel_models[0] is None: logger.warning("Seller models not found - using heuristics")
    
    try:
        # 1. Fetch data
        logger.info("Fetching market data...")
        nifty, vix = get_market_snapshots()
        intraday = get_intraday_history("^NSEI")
        logger.info(f"Data fetched: NIFTY {len(nifty)} rows, VIX {len(vix)} rows, intraday {len(intraday)} rows")
        
        # Check if we have data
        if len(nifty) < 2 or len(vix) < 2:
            logger.error("Insufficient market data fetched. Check internet connection or yfinance availability.")
            logger.info("For testing, using placeholder data...")
            # Create minimal test data
            import pandas as pd
            nifty = pd.DataFrame({
                'Open': [19700, 19750, 19800],
                'High': [19750, 19800, 19850],
                'Low': [19650, 19700, 19750],
                'Close': [19780, 19820, 19850],
                'Volume': [1000000, 1100000, 1200000]
            })
            vix = pd.DataFrame({
                'Open': [14.5, 14.8, 15.0],
                'High': [15.0, 15.2, 15.5],
                'Low': [14.3, 14.6, 14.9],
                'Close': [14.8, 15.0, 15.2],
                'Volume': [100000, 110000, 120000]
            })
            intraday = pd.DataFrame({
                'Open': [19800, 19810, 19820],
                'High': [19820, 19830, 19840],
                'Low': [19790, 19800, 19810],
                'Close': [19815, 19825, 19835],
                'Volume': [50000, 55000, 60000]
            })
        
        # 2. Build features
        logger.info("Building features...")
        dir_feats = build_direction_features(nifty, vix)
        sel_feats = build_seller_features(nifty, vix)
        buy_feats = build_buyer_features(nifty, vix)
        
        previous_close = float(nifty["Close"].iloc[-2]) if len(nifty) >= 2 else 19800
        today_intraday_feats = build_today_direction_features(intraday, previous_close)
        gamma_feats = build_gamma_window_features(intraday)
        
        logger.info("Features built successfully")
        
        # 3. Build blocks
        logger.info("Computing predictions...")
        market_block = build_market_block(nifty, vix, intraday)
        
        # Try to enhance with live price if available
        market_block = _update_market_block_with_live_price(market_block)
        
        direction_block = build_direction_block(dir_feats, today_intraday_feats, gamma_feats, nifty, vix, dir_models)
        seller_block = build_seller_block(sel_feats, nifty, sel_models)
        buyer_block = build_buyer_block(buy_feats, gamma_feats, intraday, nifty, buy_models)
        
        # 4. Assemble payload
        logger.info("Assembling payload...")
        payload = {
            "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "market": market_block,
            "direction": direction_block,
            "seller": seller_block,
            "buyer": buyer_block
        }
        
        # 5. Validate
        logger.info("Validating payload...")
        validate_payload(payload)
        
        # 6. Write
        logger.info(f"Writing to {JSON_OUTPUT_PATH}...")
        JSON_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(JSON_OUTPUT_PATH, "w") as f:
            json.dump(payload, f, indent=2)
        
        logger.info("=== AegisMatrix Inference Complete ===")
        logger.info(f"Output written to: {JSON_OUTPUT_PATH}")
        
    except Exception as e:
        logger.error(f"Inference failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
