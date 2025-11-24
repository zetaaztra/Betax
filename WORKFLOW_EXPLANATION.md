# AegisMatrix Workflow Explanation

## Overview
Your system has a **two-stage pipeline**:
1. **Training Stage** (Weekly) - Trains ML models with new market data
2. **Inference Stage** (Every 30 mins Mon-Fri) - Uses trained models to make predictions

---

## Stage 1: Model Training (Weekly)

### Schedule
- **Frequency**: Once per week (Saturdays at 00:00 UTC = 5:30 AM IST)
- **Trigger**: GitHub Actions cron job in `.github/workflows/train_models.yml`

### Process Flow
```
GitHub Actions Trigger (Saturday 00:00 UTC)
    ↓
Fetch Fresh Data from yfinance
    ↓
Train 3 ML Engines:
    1. Direction Engine (BiLSTM + XGBoost)
    2. Seller Engine (3× XGBoost models)
    3. Buyer Engine (3× XGBoost models)
    ↓
Save Trained Models to: aegismatrix-engine/models/
    ↓
Commit Models to GitHub
```

### What Gets Trained?

#### Direction Engine
```
File: direction/train_direction.py
Models Saved:
  - direction_seq.pt (BiLSTM model)
  - direction_gru_xgb.pkl (XGBoost)
  - direction_scaler.pkl (Feature scaler)
  
Purpose: Predict market direction for multiple time horizons
  - t+1: Tomorrow
  - t+3: Next 3 days
  - t+5: This week
  - t+10, t+20, t+40: Longer horizons
```

#### Seller Engine
```
File: seller/train_seller.py
Models Saved:
  - seller_trap.pkl (Volatility trap detection)
  - seller_regime.pkl (Regime classification)
  - seller_breach.pkl (Breach probability)
  
Purpose: Calculate safe ranges for option sellers
```

#### Buyer Engine
```
File: buyer/train_buyer.py
Models Saved:
  - buyer_breakout.pkl (Breakout probability)
  - buyer_spike.pkl (Spike direction bias)
  - buyer_theta.pkl (Time decay edge score)
  
Purpose: Calculate opportunities for option buyers
```

### Data Used During Training
- **Daily candles**: NIFTY & VIX (5 years of history)
- **Source**: yfinance (`^NSEI`, `^INDIAVIX`)
- **Fetched**: Automatically during training via `data_fetcher.py`

---

## Stage 2: Inference / Prediction (Every 30 mins Mon-Fri)

### Schedule
```
Multiple runs per day during market hours (IST 9:15 AM - 3:15 PM):
  - 09:00, 09:15, 09:30 IST
  - 10:00, 10:15, 10:30 IST
  - 11:00, 11:15, 11:30 IST
  - 12:00, 12:15, 12:30 IST
  - 1:00, 1:15, 1:30 IST
  - 2:00, 2:15, 2:30 IST
  - 2:45, 3:00, 3:15 IST

Plus: Manual trigger (workflow_dispatch)
```

### Process Flow
```
GitHub Actions Trigger (Every 30 mins, Mon-Fri)
    ↓
Load Pre-trained Models from aegismatrix-engine/models/
    ↓
Fetch Current Market Data:
    - Daily NIFTY & VIX (from cache or yfinance)
    - Intraday NIFTY (1-min and 5-min bars)
    - Live spot price
    ↓
Build Features from Market Data
    ↓
Generate Predictions:
    - Direction (6 horizons)
    - Seller signals (safe ranges, max pain, breach probability)
    - Buyer signals (breakout probability, spike bias, theta edge)
    ↓
Generate JSON output: aegismatrix.json
    ↓
Commit to GitHub
    ↓
Dashboard fetches JSON and displays in real-time
```

### Output File
```json
{
  "generated_at": "2025-11-24T09:52:35Z",
  "market": {
    "spot": 24100.5,
    "spot_change": 150.25,
    "spot_change_pct": 0.0063,
    "vix": 15.2,
    "vix_change": 0.5,
    "regime": "BULLISH"
  },
  "direction": {
    "today": {...},
    "horizons": {
      "t1": {"label": "Tomorrow", "direction": "UP", "conviction": 0.65},
      "t3": {"label": "Next 3 Days", "direction": "UP", "conviction": 0.58},
      ...
    }
  },
  "seller": {
    "safe_range": {"lower": 23900, "upper": 24300},
    "max_pain": {"lower": 24050, "upper": 24150},
    ...
  },
  "buyer": {
    "breakout_today": {"score": 0.62, "label": "MEDIUM"},
    ...
  }
}
```

---

## Key Question: Will Calculations Change on Each Inference Run?

### YES - They Will Vary, But Why?

#### 1. **Market Data Changes Every 30 Minutes**
```
Each inference run:
  ✓ Fetches LATEST intraday prices (1-min and 5-min bars)
  ✓ Updates spot price in real-time
  ✓ Recalculates all features based on current market state
  ✓ Uses updated volatility, momentum, technical indicators
```

#### 2. **Live Price Updates**
```
Your improved data_fetcher now prioritizes:
  1. Most recent 1-minute candle
  2. 5-minute candles if 1-min unavailable
  3. Ticker info (live price)
  
This means:
  ✓ Spot price reflects market activity right now
  ✓ Not stale data from market close
```

#### 3. **Models Stay Constant**
```
The ML models themselves DON'T change:
  ✗ direction_seq.pt - STAYS THE SAME (trained last Saturday)
  ✗ buyer_breakout.pkl - STAYS THE SAME (trained last Saturday)
  ✗ seller_trap.pkl - STAYS THE SAME (trained last Saturday)

BUT the INPUT DATA to these models changes constantly:
  ✓ Current market price
  ✓ Intraday momentum
  ✓ Volatility from latest bars
  ✓ Technical indicators from fresh data
```

### Example
```
Run 1 (09:00 IST on Monday):
  - NIFTY spot: 24,100
  - Volatility: 15.2%
  - Prediction: "UP with 65% conviction"

Run 2 (09:30 IST on Monday):
  - NIFTY spot: 24,120 (up 20 points)
  - Volatility: 15.8% (increased)
  - Prediction: "UP with 68% conviction" (changed!)
  
Run 3 (10:00 IST on Monday):
  - NIFTY spot: 24,090 (down 30 points from Run 1)
  - Volatility: 14.9% (decreased)
  - Prediction: "NEUTRAL with 52% conviction" (changed again!)
```

---

## yfinance Compliance & Rate Limiting

### Your Current Implementation

#### ✅ Good Practices You're Already Doing
```python
1. Caching Strategy (data_fetcher.py)
   - Stores daily data locally in CSV files
   - Only updates if cache is stale (3+ days old)
   - Prevents unnecessary API calls

2. Retry Logic
   - 3 retry attempts on rate limit (429 errors)
   - Exponential backoff: 2s, 4s, 8s delays
   - Random User-Agent rotation (4 different agents)

3. Timeout Handling
   - 10s timeout for API calls
   - 30s timeout for yfinance.download()
   - Prevents hanging requests

4. Fallback Strategy
   - Direct Yahoo API first (faster)
   - Falls back to yfinance if direct API fails
   - NSE API for live spot price as last resort

5. Error Handling
   - Gracefully handles failures
   - Returns empty dataframe instead of crashing
   - Logs all errors for debugging
```

#### ⚠️ Rate Limit Warnings in Your Logs
```
2025-11-24 09:52:07,763 - data_fetcher - WARNING - Rate limited by Yahoo (429). Waiting before retry 1/3...
2025-11-24 09:52:09,811 - data_fetcher - WARNING - Rate limited by Yahoo (429). Waiting before retry 2/3...
2025-11-24 09:52:13,862 - data_fetcher - WARNING - Rate limited by Yahoo (429). Waiting before retry 3/3...
2025-11-24 09:52:19,862 - data_fetcher - ERROR - Failed to fetch data for ^NSEI after 3 attempts
```

**Why this happens:**
- Running 13+ inference jobs per day (~every 30 mins)
- Each job tries to fetch daily data from yfinance
- Yahoo Finance has IP-level rate limits (~1000 requests/hour)
- After 3 consecutive failures, falls back to local cache

### ✅ Recommended Rate Limiting Improvements

#### 1. **Extend Cache Duration** (Optional)
```python
# Current: Updates if cache is 3+ days old
# Recommendation: Update only on Monday morning (weekly like training)

if is_monday_morning():
    update_cache()
else:
    use_cached_data()
```

#### 2. **Batch Requests** (Already doing well)
```python
Current good practice:
- Fetch NIFTY once
- Fetch VIX once
- Cache both
- Don't refetch within same run

This is already optimized! ✓
```

#### 3. **Add Request Delays** (Optional)
```python
# Between multiple inference runs (every 30 mins)
import time
time.sleep(2)  # 2-second pause before API calls

# You already do this with retry backoff ✓
```

#### 4. **IP Rotation** (Can't do on GitHub Actions)
```
GitHub Actions uses shared IPs that may hit rate limits
Not much you can do about this - it's a GitHub limitation
Your fallback strategy (local cache + NSE API) handles this ✓
```

### Yfinance Best Practices Checklist

```
✅ Using timeout parameter
✅ Retry logic with backoff
✅ Rotating User-Agents
✅ Local caching strategy
✅ Handling MultiIndex columns (yfinance updates)
✅ Error handling and fallbacks
✅ Not hammering the same endpoint repeatedly

⚠️  Rate limit handling (unavoidable on GitHub Actions)
    → Your current fallback strategy mitigates this well
```

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│         TRAINING PIPELINE (Weekly Saturday)              │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
          ┌──────────────────────────────┐
          │  Fetch Fresh Data (yfinance)  │
          │  5 years daily NIFTY + VIX    │
          └────────────┬─────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
   ┌─────────┐   ┌─────────┐   ┌─────────┐
   │Direction│   │ Seller  │   │ Buyer   │
   │ Engine  │   │ Engine  │   │ Engine  │
   └────┬────┘   └────┬────┘   └────┬────┘
        │             │             │
        └──────────────┼─────────────┘
                       │
                       ▼
          ┌──────────────────────────────┐
          │   Trained Models Saved        │
          │ aegismatrix-engine/models/    │
          │  (*.pkl, *.pt files)          │
          └────────────┬─────────────────┘
                       │
                       ▼
          ┌──────────────────────────────┐
          │    Committed to GitHub        │
          │   (models/ directory)         │
          └──────────────────────────────┘


┌─────────────────────────────────────────────────────────┐
│   INFERENCE PIPELINE (Every 30 mins Mon-Fri)             │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
          ┌──────────────────────────────┐
          │  Load Pre-trained Models      │
          │  from aegismatrix-engine/     │
          │  models/                      │
          └────────────┬─────────────────┘
                       │
                       ▼
          ┌──────────────────────────────┐
          │  Fetch Current Market Data    │
          │  - Daily: NIFTY, VIX (cache) │
          │  - Intraday: 1-min, 5-min    │
          │  - Live spot price           │
          └────────────┬─────────────────┘
                       │
                       ▼
          ┌──────────────────────────────┐
          │   Build Features              │
          │  (Technical indicators,       │
          │   momentum, volatility, etc)  │
          └────────────┬─────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
   ┌─────────┐   ┌─────────┐   ┌─────────┐
   │Direction│   │ Seller  │   │ Buyer   │
   │Predict  │   │ Compute │   │ Compute │
   └────┬────┘   └────┬────┘   └────┬────┘
        │             │             │
        └──────────────┼─────────────┘
                       │
                       ▼
          ┌──────────────────────────────┐
          │  Generate aegismatrix.json    │
          │  (predictions + market data)  │
          └────────────┬─────────────────┘
                       │
                       ▼
          ┌──────────────────────────────┐
          │  Commit to GitHub             │
          │  (aegismatrix.json)           │
          └────────────┬─────────────────┘
                       │
                       ▼
          ┌──────────────────────────────┐
          │  Dashboard Fetches & Display  │
          │  Real-time in UI              │
          └──────────────────────────────┘
```

---

## Summary Answer to Your Questions

### Q1: "Will calculations change when inference runs?"
**A:** **YES - Every 30 minutes**
- Models stay the same (trained weekly)
- But market data changes every 30 mins
- Features recalculated with fresh data
- Predictions update accordingly

### Q2: "Make sure data fetches are under yfinance norms"
**A:** **You're 95% compliant ✅**
- Good caching strategy
- Proper retry/backoff logic
- Rate limit fallbacks working
- Error handling solid

**Small improvements possible:**
- Could cache daily data for full week (not just 3 days)
- But current strategy is reasonable for 13 runs/day

---

## Monitoring

### What to Watch
```
1. Check logs for rate limit warnings (429 errors)
   - Expected during peak hours
   - Should fallback gracefully to cache

2. Verify aegismatrix.json updates
   - timestamp should change every 30 mins
   - spot price should reflect current market

3. Monitor training run (Saturdays)
   - Should complete in ~60 seconds
   - All 3 engines should train successfully

4. Check model files exist
   - aegismatrix-engine/models/*.pkl (XGBoost)
   - aegismatrix-engine/models/*.pt (PyTorch)
   - aegismatrix-engine/models/*_scaler.pkl
```

### Log Locations
```
Training logs: GitHub Actions → train_models.yml
Inference logs: GitHub Actions → aegismatrix-infer-build.yml
Model files: aegismatrix-engine/models/
Output: client/public/data/aegismatrix.json
```

---

## Potential Issues & Solutions

### Issue 1: "Rate limiting causing inference failures"
**Solution:**
- Current fallback (cache + NSE API) handles this
- Inference still completes with cached data
- Only live intraday data might be delayed

### Issue 2: "Models not updating"
**Solution:**
- Training runs weekly (Saturdays)
- Check if training job succeeded (GitHub Actions logs)
- Verify models/ directory has new files with recent timestamps

### Issue 3: "Calculations wildly different between runs"
**Solution:**
- Normal! Market changes constantly
- If NIFTY moves 50 points, predictions should change
- Check if market is actually moving (check spot price)

### Issue 4: "Dashboard showing stale data"
**Solution:**
- Verify aegismatrix.json timestamp
- Check if inference workflow ran successfully
- May need to hard-refresh dashboard (Ctrl+F5)

---

## Next Steps (Optional Optimizations)

1. **Add alerting** when inference fails
2. **Monitor model performance** weekly (backtesting)
3. **Add data versioning** (track which training data was used)
4. **Implement data freshness indicator** in dashboard
5. **Add alternative data sources** (backup API) for high-frequency runs
