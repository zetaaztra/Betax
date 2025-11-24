# Visual Comparison: Training vs Inference

## Side-by-Side Comparison

```
╔════════════════════════════════════════════════════════════════════════════╗
║                     TRAINING vs INFERENCE PIPELINE                         ║
╚════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────┬─────────────────────────────────────┐
│            TRAINING (Weekly)            │        INFERENCE (Every 30 mins)    │
├─────────────────────────────────────────┼─────────────────────────────────────┤
│                                         │                                     │
│ TRIGGER                                 │ TRIGGER                             │
│ ├─ Cron: Saturday 00:00 UTC             │ ├─ Cron: Mon-Fri, 9:00-3:15 PM    │
│ ├─ Manual: workflow_dispatch            │ ├─ Manual: workflow_dispatch        │
│                                         │                                     │
│ MODELS                                  │ MODELS                              │
│ ├─ Loading: Create new models           │ ├─ Loading: Load pre-trained       │
│ ├─ Training: Learn from data            │ ├─ Usage: Apply learned patterns    │
│ └─ Saving: Save trained weights         │ └─ Storage: Use existing weights    │
│                                         │                                     │
│ DATA INPUT                              │ DATA INPUT                          │
│ ├─ Timespan: 5 years (2020-2025)       │ ├─ Timespan: Today + intraday      │
│ ├─ Rows: ~1,234 daily candles          │ ├─ Rows: Few hundred intraday      │
│ ├─ Freshness: Whatever yfinance has    │ ├─ Freshness: Real-time (1-5 min)  │
│ └─ Focus: Long-term patterns            │ └─ Focus: Current conditions        │
│                                         │                                     │
│ COMPUTATION                             │ COMPUTATION                         │
│ ├─ Type: Heavy (GPU-friendly)          │ ├─ Type: Light (CPU-friendly)      │
│ ├─ Duration: ~60 seconds               │ ├─ Duration: ~30 seconds           │
│ ├─ Memory: High (large tensors)        │ ├─ Memory: Low (just inference)    │
│ └─ Steps: Train → Validate → Save      │ └─ Steps: Load → Predict → Export  │
│                                         │                                     │
│ OUTPUT                                  │ OUTPUT                              │
│ ├─ Type: Model files                    │ ├─ Type: JSON predictions          │
│ ├─ Files: ~9 files (*.pkl, *.pt)       │ ├─ File: aegismatrix.json          │
│ ├─ Size: ~900KB total                  │ ├─ Size: ~4KB                      │
│ └─ Example: direction_seq.pt            │ └─ Example: spot=24100, pred=UP    │
│                                         │                                     │
│ COMMITS                                 │ COMMITS                             │
│ ├─ What: Models directory               │ ├─ What: JSON output               │
│ ├─ Frequency: Once per week             │ ├─ Frequency: 13x per week         │
│ ├─ Message: "update trained models"    │ ├─ Message: "update predictions"   │
│ └─ Size: ~900KB per commit              │ └─ Size: ~4KB per commit           │
│                                         │                                     │
│ STABILITY                               │ STABILITY                           │
│ ├─ Model Weights: FROZEN after save    │ ├─ Model Weights: UNCHANGED        │
│ ├─ Predictions: Change only if train    │ ├─ Predictions: Change constantly  │
│ ├─ Reason: New training algorithm       │ ├─ Reason: New market conditions   │
│ └─ Frequency: Once per week             │ └─ Frequency: Every 30 minutes     │
│                                         │                                     │
└─────────────────────────────────────────┴─────────────────────────────────────┘
```

---

## The Key Difference Explained

```
┌──────────────────────────────────────────────────────────────────────┐
│                         ML PIPELINE ANALOGY                          │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  TRAINING = Building a Weather Forecast Model                       │
│  ═══════════════════════════════════════════════════════            │
│                                                                      │
│  Process:                                                            │
│  1. Collect 5 years of weather data                                 │
│  2. Find patterns: "When pressure drops, rain comes"                │
│  3. Build prediction algorithm from patterns                         │
│  4. Save algorithm (frozen, won't change)                           │
│                                                                      │
│  Result: Trained model (algorithm with learned weights)             │
│                                                                      │
│  ─────────────────────────────────────────────────────              │
│                                                                      │
│  INFERENCE = Using Weather Model for Daily Predictions              │
│  ══════════════════════════════════════════════════════             │
│                                                                      │
│  Process:                                                            │
│  1. Load saved algorithm (from training)                            │
│  2. Get TODAY'S pressure reading                                    │
│  3. Apply algorithm to today's pressure                             │
│  4. Output today's forecast                                         │
│                                                                      │
│  Result: Daily prediction (different each day because weather       │
│           changes, but algorithm stays the same)                    │
│                                                                      │
│  ─────────────────────────────────────────────────────              │
│                                                                      │
│  WHY PREDICTIONS CHANGE:                                            │
│  • Algorithm is frozen ✓ (trained once per week)                    │
│  • But input data changes ✓ (market moves every 30 mins)            │
│  • Different input → Different output                               │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Timeline Visualization

```
WEEK VIEW (One Complete Cycle)
═════════════════════════════════════════════════════════════════════

Monday
├─ 09:00: Inference → JSON update
├─ 09:30: Inference → JSON update (different from 09:00)
├─ 10:00: Inference → JSON update (different from 09:30)
├─ 10:30: Inference → JSON update
├─ 11:00: Inference → JSON update
├─ ... (repeats every 30 mins)
└─ 15:30: Last inference of the day

Tuesday - Friday
├─ ... (same pattern, 13 inference runs per day)
└─ Each produces DIFFERENT predictions (market changed)

Saturday 00:00 UTC (5:30 AM IST)
├─ Training job starts
│  ├─ Fetch 5 years fresh data
│  ├─ Train Direction model
│  ├─ Train Seller models
│  ├─ Train Buyer models
│  └─ Save all models
├─ Models committed to GitHub
├─ Previous models REPLACED (new training complete)
└─ Sunday-Friday uses these new models

Next Monday 09:00
├─ Inference loads Saturday's NEW trained models
├─ Uses TODAY'S market data
├─ Generates predictions
└─ Cycle continues...

KEY INSIGHT:
────────────
Models change once per week (Saturday)
Predictions change 13x per week (every 30 mins Mon-Fri)
Both because of different reasons!

Model change reason: New training data/algorithm
Prediction change reason: New market conditions
```

---

## Concrete Example: 3 Consecutive Runs

```
╔════════════════════════════════════════════════════════════════════════╗
║              MONDAY 9:00-10:00 AM: Three Consecutive Runs             ║
╚════════════════════════════════════════════════════════════════════════╝

RUN 1: 9:00 AM
───────────────────────────────────────────────────────────────────────

Input:
  ├─ Direction Model: direction_seq.pt (Saturday's training)
  ├─ Buyer Model: buyer_breakout.pkl (Saturday's training)
  ├─ Seller Model: seller_trap.pkl (Saturday's training)
  ├─ NIFTY Close: 24,100.00
  ├─ 5-min Candles: [9:15, 9:20, 9:25, ..., 8:55]
  ├─ Volatility: 15.2%
  └─ RSI(14): 58

Processing:
  ├─ Build features from current data
  ├─ Normalize features (using trained scaler)
  ├─ Feed to Direction model
  ├─ Feed to Buyer model
  └─ Feed to Seller model

Output:
  ├─ Spot Price: 24,100.00
  ├─ Direction: UP (conviction: 0.65)
  ├─ Buyer Breakout: MEDIUM (score: 0.62)
  ├─ Seller Safe Range: [23,950 - 24,250]
  └─ Generated at: 09:00:35


RUN 2: 9:30 AM
───────────────────────────────────────────────────────────────────────

Input:
  ├─ Direction Model: direction_seq.pt (SAME)
  ├─ Buyer Model: buyer_breakout.pkl (SAME)
  ├─ Seller Model: seller_trap.pkl (SAME)
  ├─ NIFTY Close: 24,150.00 ← CHANGED! (+50 points)
  ├─ 5-min Candles: [9:45, 9:40, 9:35, ..., 9:10] ← FRESH DATA!
  ├─ Volatility: 15.8% ← CHANGED!
  └─ RSI(14): 62 ← CHANGED!

Processing:
  ├─ Build features from CURRENT (different) data
  ├─ Normalize features (using same trained scaler)
  ├─ Feed to Direction model (same model, different input)
  ├─ Feed to Buyer model (same model, different input)
  └─ Feed to Seller model (same model, different input)

Output:
  ├─ Spot Price: 24,150.00 ← DIFFERENT
  ├─ Direction: UP (conviction: 0.72) ← DIFFERENT
  ├─ Buyer Breakout: MEDIUM-HIGH (score: 0.68) ← DIFFERENT
  ├─ Seller Safe Range: [23,980 - 24,320] ← DIFFERENT
  └─ Generated at: 09:30:42


RUN 3: 10:00 AM
───────────────────────────────────────────────────────────────────────

Input:
  ├─ Direction Model: direction_seq.pt (SAME)
  ├─ Buyer Model: buyer_breakout.pkl (SAME)
  ├─ Seller Model: seller_trap.pkl (SAME)
  ├─ NIFTY Close: 24,050.00 ← CHANGED AGAIN! (-100 from 9:30)
  ├─ 5-min Candles: [10:15, 10:10, 10:05, ..., 9:40] ← MORE FRESH DATA!
  ├─ Volatility: 14.9% ← CHANGED!
  └─ RSI(14): 45 ← CHANGED!

Processing:
  ├─ Build features from CURRENT (again different) data
  ├─ Normalize features (using same trained scaler)
  ├─ Feed to Direction model (same model, different input again)
  ├─ Feed to Buyer model (same model, different input again)
  └─ Feed to Seller model (same model, different input again)

Output:
  ├─ Spot Price: 24,050.00 ← DIFFERENT AGAIN
  ├─ Direction: NEUTRAL (conviction: 0.55) ← CHANGED SIGNIFICANTLY
  ├─ Buyer Breakout: LOW-MEDIUM (score: 0.48) ← CHANGED
  ├─ Seller Safe Range: [23,900 - 24,200] ← CHANGED
  └─ Generated at: 10:00:38


SUMMARY
───────────────────────────────────────────────────────────────────────

Models: UNCHANGED (same *.pkl and *.pt files)
Market: CHANGED (NIFTY moved -50 to +50 points in one hour)
Features: CHANGED (calculated from new market data)
Predictions: CHANGED (different because features changed)

This is CORRECT BEHAVIOR! ✅

Models don't need to change just because market moved.
But predictions MUST change to reflect market movement.
```

---

## Troubleshooting Decision Tree

```
                          Issue Detected?
                                │
                ┌───────────────┼───────────────┐
                │               │               │
        Inference Failed    Models Wrong      Spot Price Stale
                │               │               │
        ┌───────┴───────┐   ┌───┴────┐   ┌─────┴─────┐
        │               │   │        │   │           │
   Error in      Failed to  Saturday New   Cache not  Live price
   logs?         get data?  train job?  updated?     fetch failed?
        │               │        │        │           │
       YES             YES       YES      YES         YES
        │               │        │        │           │
    Check rate Check    Check  Clear    Use NSE
    limit     cache     GitHub cache &  API
    errors    files     logs   retrain  fallback
        │               │        │        │
        └───────────────┴────────┴────────┘
                        │
                 Problem Solved?
                        │
                       YES ✓
```

---

## Key Takeaways

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  1. Models trained ONCE per week (Saturday)                      ┃
┃     └─ So models are constant during the week                    ┃
┃                                                                  ┃
┃  2. Predictions generated 13× per week (Mon-Fri every 30 mins)  ┃
┃     └─ So predictions change constantly                         ┃
┃                                                                  ┃
┃  3. Market data fetched FRESH every 30 mins                     ┃
┃     └─ So predictions adapt to market movement                  ┃
┃                                                                  ┃
┃  4. yfinance compliant with caching & backoff                   ┃
┃     └─ So no rate limit issues (graceful fallback)              ┃
┃                                                                  ┃
┃  5. This is all WORKING AS DESIGNED! ✅                         ┃
┃     └─ Predictions should change with market                    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

---

## File Size Comparison

```
Weekly Training Output (~900 KB)
├─ direction_seq.pt ..................... 500 KB (BiLSTM weights)
├─ direction_scaler.pkl .................. 1 KB (Feature scaler)
├─ direction_gru_xgb.pkl ................100 KB (XGBoost)
├─ buyer_breakout.pkl ...................100 KB (XGBoost)
├─ buyer_spike.pkl ......................100 KB (XGBoost)
├─ buyer_theta.pkl ......................100 KB (XGBoost)
├─ seller_trap.pkl .......................50 KB (XGBoost)
├─ seller_regime.pkl .....................50 KB (XGBoost)
└─ seller_breach.pkl .....................50 KB (XGBoost)

Daily Inference Output (Every 30 mins, ~4 KB)
└─ aegismatrix.json ........................4 KB (Current predictions)
   ├─ market data (spot, vix, regime)
   ├─ direction predictions (6 horizons)
   ├─ seller calculations (safe ranges, breach prob)
   └─ buyer calculations (breakout, spike, theta)

Ratio: Models (900 KB) : Predictions (4 KB) = 225 : 1
```

---

## Final Answer Summary

```
YOUR QUESTIONS                    OUR ANSWERS
═════════════════════════════════════════════════════════════════

"Will calculations change        YES - Market changes every 30 mins
 when infer runs?"               Models stay same but market data
                                 is fresh, so predictions change

"Make sure data fetches         ✅ You're already compliant:
 under yfinance norms"          - Proper caching (3-day TTL)
                                - Exponential backoff on rate limits
                                - Timeouts and error handling
                                - User-Agent rotation
                                - Graceful fallbacks to cache
                                - No commercial use

"Is this setup correct?"        ✅ YES! Perfect setup:
                                - Train weekly (Saturday)
                                - Infer frequently (every 30 min)
                                - Model weights constant
                                - Market data always fresh
                                - Predictions responsive to market
                                - System handles failures well
```
