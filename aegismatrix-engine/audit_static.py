
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import numpy as np
from infer import build_seller_block, build_buyer_block
from seller.model import compute_breach_probability_curve
from buyer.model import compute_breakout_levels
import logging

logging.basicConfig(level=logging.INFO)

def audit():
    print("--- Auditing Static Values ---")
    
    # Mock Data
    nifty = pd.DataFrame({"Close": [26000.0, 26100.0]})
    vix = pd.DataFrame({"Close": [12.0, 12.5]})
    
    # 1. Check Historical Hit Rates in infer.py
    # We need to mock models as None to trigger fallbacks or just check the function output
    print("\n[Audit 1] Historical Hit Rates")
    # These are hardcoded in build_seller_block and build_buyer_block
    # We can't easily import them without running the whole block logic which requires features
    # So we will just inspect the code or rely on my previous read.
    # But let's try to run the block builders with dummy features
    
    sel_feats = pd.DataFrame({"vol_20d": [0.01], "Close": [26100], "ret_1d": [0.001]})
    buy_feats = pd.DataFrame({"vol_20d": [0.01], "Close": [26100], "ret_5d": [0.005]})
    
    # Mock models
    sel_models = (None, None, None)
    buy_models = (None, None, None)
    
    try:
        sb = build_seller_block(sel_feats, nifty, sel_models)
        print(f"Seller Historical Hit Rate: {sb.get('historical_hit_rate')}")
        if sb.get('historical_hit_rate') != 0.72:
             print(">> SUCCESS: Seller hit rate is dynamic (changed from default 0.72)")
        
        bb = build_buyer_block(buy_feats, [], pd.DataFrame(), nifty, buy_models)
        print(f"Buyer Historical Spike Rate: {bb.get('historical_spike_rate')}")
        if bb.get('historical_spike_rate') != 0.58:
             print(">> SUCCESS: Buyer spike rate is dynamic (changed from default 0.58)")
             
    except Exception as e:
        print(f"Block build failed: {e}")

    # 2. Check Breach Distances
    print("\n[Audit 2] Breach Distances")
    breach = compute_breach_probability_curve(26100, 0.15, 30, None, sel_feats)
    distances = [b['distance'] for b in breach]
    print("Breach Curve Distances:", distances)
    
    # Expected: 0.5%, 1%, 1.5%, 2% of 26100 -> 130, 261, 391, 522
    if distances[0] != 100:
        print(">> SUCCESS: Breach distances are dynamic (not fixed 100, 200...)")
    
    # 3. Check Breakout Levels Fallback
    print("\n[Audit 3] Breakout Levels Fallback")
    # Pass empty nifty to trigger fallback
    # But pass features with Close=26100
    levels = compute_breakout_levels(buy_feats, {})
    print(f"Fallback Breakout Levels (Empty Nifty, Feats=26100): {levels}")
    
    # Expected center around 26100, not 26000
    mid = (levels['upper'] + levels['lower']) / 2
    if abs(mid - 26100) < 1:
        print(">> SUCCESS: Fallback used feature price (26100) instead of hardcoded 26000")

if __name__ == "__main__":
    audit()
