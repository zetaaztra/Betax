# Quick Reference: Your System Checklist

## What Happens When

### Every Saturday 00:00 UTC (5:30 AM IST)
- ✅ **Training Job Runs**
- Fetches 5 years of NIFTY + VIX data from yfinance
- Trains 3 engines (Direction, Seller, Buyer)
- Saves ~9 model files to `aegismatrix-engine/models/`
- Commits models to GitHub
- **Duration:** ~60 seconds

### Every 30 Minutes (Mon-Fri, 9 AM - 3:30 PM IST)
- ✅ **Inference Job Runs**
- Loads last week's trained models
- Fetches current market data (daily from cache, intraday fresh)
- Generates predictions using models
- Saves to `aegismatrix.json`
- Commits to GitHub
- Dashboard updates
- **Duration:** ~30 seconds

---

## Will Calculations Change?

| Aspect | Changes? | Why? |
|--------|----------|------|
| **Models** | ❌ NO | Retrained only weekly |
| **Market Data** | ✅ YES | Fetched fresh every 30 mins |
| **Features** | ✅ YES | Recalculated from new market data |
| **Predictions** | ✅ YES | Result of using new features |
| **Spot Price** | ✅ YES | Updated from latest trades |

**Example:**
```
9:00 AM: NIFTY=24,100 → Prediction: UP (65% confidence)
9:30 AM: NIFTY=24,150 → Prediction: UP (72% confidence)
10:00 AM: NIFTY=24,050 → Prediction: NEUTRAL (55% confidence)
```

---

## yfinance Compliance Status

### ✅ You're Doing Right
- Caching daily data (prevents hammering API)
- Retry with backoff (handles temporary failures)
- Random User-Agent rotation
- Proper timeouts (10s-30s)
- Error handling (graceful fallbacks)
- NSE API fallback for live data

### ⚠️ Rate Limit Handling
```
Your logs show:
"Rate limited by Yahoo (429). Waiting before retry 1/3..."

This is EXPECTED and NORMAL because:
- Running 13 inference jobs daily
- Each tries to fetch daily data
- Yahoo has IP-level limits

Your system HANDLES THIS correctly:
- Retries 3 times (spacing delays: 2s, 4s, 8s)
- Falls back to cached data
- Inference completes successfully
✅ No action needed
```

### Compliant with yfinance Terms
- ✅ Not storing data commercially
- ✅ Respectful rate limiting with backoff
- ✅ Proper error handling
- ✅ Timeout settings

---

## File Locations

```
TRAINING ARTIFACTS:
  aegismatrix-engine/
    ├── models/
    │   ├── direction_seq.pt          (BiLSTM)
    │   ├── direction_gru_xgb.pkl     (XGBoost)
    │   ├── direction_scaler.pkl
    │   ├── buyer_breakout.pkl
    │   ├── buyer_spike.pkl
    │   ├── buyer_theta.pkl
    │   ├── seller_trap.pkl
    │   ├── seller_regime.pkl
    │   └── seller_breach.pkl
    └── data/                         (Cached market data)
        ├── NSEI_daily.csv
        ├── INDIAVIX_daily.csv
        ├── NSEI_intraday.csv
        └── *.csv

OUTPUT:
  client/public/data/
    └── aegismatrix.json             (Latest predictions)

WORKFLOWS:
  .github/workflows/
    ├── train_models.yml             (Weekly)
    └── aegismatrix-infer-build.yml  (Every 30 mins)
```

---

## Monitoring Dashboard

### What to Check Weekly
```
☑️ Training Job (Saturday)
   - Status: Succeeded or Failed?
   - Log: Any errors?
   - Duration: ~60 seconds?
   - Models: Updated timestamps?

☑️ Inference Jobs (Mon-Fri)
   - Status: How many succeeded?
   - Any 429 rate limit errors?
   - aegismatrix.json size: > 3KB?

☑️ Model Performance
   - Spot price updates in real-time?
   - Predictions change as market moves?
   - No stale timestamps?
```

### GitHub Actions Links
```
Training: https://github.com/zetaaztra/Betax/actions/workflows/train_models.yml
Inference: https://github.com/zetaaztra/Betax/actions/workflows/aegismatrix-infer-build.yml
```

---

## Common Scenarios

### Scenario 1: Inference Ran But No JSON Update
**Check:**
- Did GitHub Actions job succeed? (see Actions tab)
- Is JSON file being committed? (see commits)
- Dashboard hard-refresh needed? (Ctrl+F5)

### Scenario 2: Predictions Seem Wrong
**Expected!** Market changes constantly
- NIFTY moved 50 points? Predictions will change
- It's not wrong, it's working correctly

### Scenario 3: 429 Rate Limit Errors in Logs
**Normal!** GitHub IP hitting limits
- Job still completes (uses cached data)
- Live intraday data might be slightly delayed
- No action needed

### Scenario 4: Models Not Updating
**Check:**
- Did training job run Saturday? (Actions tab)
- Did it succeed? (check logs)
- Are new model files committed? (check commit history)

---

## Quick Fixes

### If Inference Fails
```bash
# Manual trigger in GitHub Actions
1. Go to Actions tab
2. Click "aegismatrix-infer-build.yml"
3. Click "Run workflow"
4. Select "main" branch
5. Click green "Run workflow" button
```

### If Training Fails
```bash
# Manual trigger in GitHub Actions
1. Go to Actions tab
2. Click "train_models.yml"
3. Click "Run workflow"
4. Select "main" branch
5. Click green "Run workflow" button
```

### If Models Missing
```bash
# Ensure models are committed
git status aegismatrix-engine/models/
git add aegismatrix-engine/models/
git commit -m "Add trained models"
git push
```

---

## Summary

| Question | Answer | Details |
|----------|--------|---------|
| **Will calculations change?** | ✅ YES | Every 30 mins, new market data → new predictions |
| **Do models change daily?** | ❌ NO | Models retrain only weekly (Saturdays) |
| **Is rate limiting an issue?** | ⚠️ MANAGED | You have proper fallback strategy |
| **Is yfinance being respected?** | ✅ YES | Caching, retry logic, timeouts all good |
| **What commits to GitHub?** | 📄 Two Things | Training: model files, Inference: aegismatrix.json |
| **How often to monitor?** | 📅 Weekly | Check Saturday training, then daily inference runs |

---

## Architecture Summary
```
┌─────────────────────────────────────────┐
│          Trained Models (Constant)       │
│  - Direction (6 time horizons)          │
│  - Seller (safe ranges, max pain)       │
│  - Buyer (breakout, spike, theta)       │
└────────────┬────────────────────────────┘
             │
             │ Fixed Models
             ▼
┌─────────────────────────────────────────┐
│      + Fresh Market Data (Changes)       │
│  - Spot price (updates 1-2 sec)         │
│  - Volatility (updates 5-min)           │
│  - Technical indicators (updates 5-min) │
└────────────┬────────────────────────────┘
             │
             │ Combines → Different output
             ▼
┌─────────────────────────────────────────┐
│     New Predictions Every 30 Minutes     │
│       (aegismatrix.json updates)        │
└─────────────────────────────────────────┘
```

This is why **calculations change even though models stay the same!**
