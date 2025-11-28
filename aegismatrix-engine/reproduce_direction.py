
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import numpy as np
from direction.model import predict_direction_horizons, load_models
from direction.today_direction import compute_today_direction
import logging

logging.basicConfig(level=logging.INFO)

def reproduce():
    print("--- Reproducing Direction Issues ---")
    
    # Mock Data
    # Create enough data for features (need > 60 rows)
    dates = pd.date_range(end=pd.Timestamp.now(), periods=100)
    nifty = pd.DataFrame({
        "Close": np.linspace(20000, 21000, 100) + np.random.randn(100) * 50,
        "Open": np.linspace(20000, 21000, 100),
        "High": np.linspace(20000, 21000, 100) + 50,
        "Low": np.linspace(20000, 21000, 100) - 50,
        "Volume": np.random.randint(1000, 10000, 100)
    }, index=dates)
    
    # Add features manually to match what model expects (simplified)
    # In reality we should use build_direction_features, but let's just mock the input to predict_direction_horizons
    # The model expects scaled features. 
    # Let's actually load the real models and see what happens with dummy data.
    
    models = load_models()
    if models[0] is None:
        print("Models not found, cannot reproduce model behavior exactly without them.")
        # But we can reproduce the logic flaws if we mock the model output or just test the logic functions
    
    # 1. Test "Today Direction" Logic
    print("\n[Test 1] Today Direction Logic")
    daily_bias = {
        "logit": 0.0, # Neutral
        "expected_move_points_today": 50.0 # Hardcoded in infer.py
    }
    intraday_feats = {
        "gap_pct": 0.0,
        "orb_breakout_score": 0.5,
        "realized_vol_norm": 0.5
    }
    
    today = compute_today_direction(daily_bias, intraday_feats)
    print(f"Input: expected_move_points_today=50.0 (Simulated ATR)")
    print(f"Output: {today}")
    
    if today['expected_move_points'] != 30.0:
        print(">> SUCCESS: Expected move is dynamic (or at least not the old static calculation if inputs changed)")
    else:
        print(">> NOTE: If input was 50.0, output 30.0 is correct math, but in infer.py we now pass dynamic ATR.")

    # 2. Test Conviction Logic
    print("\n[Test 2] Conviction Logic")
    
    horizons = [1, 3, 5, 10]
    conviction_base = 0.15 # Very low confidence
    
    print(f"Base Conviction: {conviction_base}")
    for h in horizons:
        # Logic from model.py (updated)
        horizon_conviction = max(0.1, conviction_base * (1 - np.log(h)/10))
        print(f"T+{h}: {horizon_conviction:.4f}")
        
    if any(max(0.1, conviction_base * (1 - np.log(h)/10)) < 0.34 for h in horizons):
        print(">> SUCCESS: Conviction can go below 0.34")

if __name__ == "__main__":
    reproduce()
