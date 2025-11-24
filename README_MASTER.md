# 🚀 AEGIS Dashboard - Complete Documentation

**Last Updated:** November 24, 2025  
**Status:** ✅ Fully Operational (After numpy compatibility fix)  
**Repository:** Betax (zetaaztra/Betax)

---

## 📋 TABLE OF CONTENTS

1. [Quick Start](#quick-start)
2. [System Overview](#system-overview)
3. [Issue & Resolution](#issue--resolution)
4. [Project Structure](#project-structure)
5. [Code Statistics](#code-statistics)
6. [Backend Setup](#backend-setup)
7. [Frontend Setup](#frontend-setup)
8. [API Documentation](#api-documentation)
9. [Training Pipeline](#training-pipeline)
10. [Inference Pipeline](#inference-pipeline)
11. [GitHub Actions Workflow](#github-actions-workflow)
12. [Troubleshooting](#troubleshooting)
13. [FAQ](#faq)

---

## 🏃 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- npm or yarn
- Git

### Installation

**Backend (Python):**
```bash
cd aegismatrix-engine
pip install -r requirements.txt
python train_all.py  # Train models
python infer.py      # Run inference
```

**Frontend (React + TypeScript):**
```bash
npm install
npm run dev          # Development
npm run build        # Production
```

### First Run
```bash
# 1. Train models
python train_all.py

# 2. Run inference
python infer.py

# 3. Start frontend
npm run dev

# 4. Open browser
# http://localhost:5173
```

---

## 🎯 System Overview

### What This System Does

**AEGIS Dashboard** is an AI-powered options market analysis and prediction system that:

✅ **Fetches real-time market data** from yfinance  
✅ **Calculates 50+ technical features** every 30 minutes  
✅ **Trains 7 ML models** weekly (Direction, Seller, Buyer engines)  
✅ **Predicts market movements** for 1-day, 3-day, and 1-week horizons  
✅ **Analyzes option seller risk** (volatility traps, expiry stress)  
✅ **Identifies buyer opportunities** (breakouts, spikes, theta edge)  
✅ **Updates dashboard in real-time** with live predictions  

### Architecture

```
┌─────────────────────────────────────────────────────┐
│                    GitHub Actions                   │
│  ┌────────────────────────────────────────────────┐ │
│  │ Saturday:  python train_all.py (weekly)        │ │
│  │ Mon-Fri:   python infer.py (every 30 min)      │ │
│  └────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
         ↓
    aegismatrix.json
         ↓
┌─────────────────────────────────────────────────────┐
│              Frontend (React + TypeScript)           │
│  ┌────────────────────────────────────────────────┐ │
│  │ Dashboard with real-time market data           │ │
│  │ - Spot price & VIX                             │ │
│  │ - Direction predictions                        │ │
│  │ - Option seller analysis                       │ │
│  │ - Buyer opportunity detection                  │ │
│  └────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

---

## 🔧 Issue & Resolution

### THE PROBLEM (Before November 24, 2025)

**Symptom:** Dashboard showed:
- ✅ Spot price: CHANGING (Good!)
- ✅ VIX: CHANGING (Good!)
- ❌ Volatility Trap: ALWAYS 0.95 (Bad!)
- ❌ Expiry Stress: ALWAYS 0.15 (Bad!)
- ❌ Historical rates: ALWAYS 72%, 58% (Bad!)

**Root Cause:** 
```
Models trained with numpy 1.x
System updated to numpy 2.x
Pickle incompatibility: "No module named 'numpy._core'"
Models fail to load → Fallback to heuristics → Static values
```

**Visual Explanation:**
```
BEFORE FIX:
Inference runs → Try to load models → 
ERROR (numpy._core not found) → 
Use dumb backup calculation → 
Same value every time ❌

AFTER FIX:
Inference runs → Load models successfully → 
Use smart AI prediction → 
Different value each time ✅
```

### THE SOLUTION

**Command:**
```bash
cd aegismatrix-engine
python train_all.py
```

**What Happens:**
1. Models retrained with numpy 2.x
2. Saved with new compatibility
3. Next inference: Models load successfully ✅
4. Smart predictions work again ✅
5. Dashboard shows dynamic values ✅

**Result:** All metrics now update every 30 minutes!

### Verification

```bash
# Check if models load
python -c "
from seller.model import load_models
t, r, b = load_models()
print('✅ Fixed!' if all([t,r,b]) else '❌ Broken')
"
```

---

## 📁 Project Structure

```
aegis-dashboard/
│
├── 📂 aegismatrix-engine/          # Backend: ML models & inference
│   ├── config.py                   # Configuration (data paths, horizons)
│   ├── data_fetcher.py             # Fetch market data from yfinance
│   ├── infer.py                    # Inference script (main)
│   ├── train_all.py                # Training script (weekly)
│   ├── schema.py                   # Data schemas
│   ├── test_api.py                 # Testing utilities
│   │
│   ├── 📂 direction/               # Direction prediction engine
│   │   ├── model.py                # Direction ML model (BiLSTM)
│   │   └── today_direction.py      # Today-specific predictions
│   │
│   ├── 📂 seller/                  # Seller option analytics
│   │   ├── model.py                # Seller ML models (trap, regime, breach)
│   │   └── features.py             # Seller feature engineering
│   │
│   ├── 📂 buyer/                   # Buyer opportunity detection
│   │   ├── model.py                # Buyer ML models
│   │   └── features.py             # Buyer feature engineering
│   │
│   ├── 📂 features/                # Feature engineering
│   │   ├── daily_features.py       # Daily features (momentum, vol)
│   │   └── intraday_features.py    # Intraday features (gamma, theta)
│   │
│   ├── 📂 shared/                  # Shared utilities
│   │   ├── utils.py                # Common functions
│   │   └── helpers.py              # Helper functions
│   │
│   ├── 📂 models/                  # Trained ML models
│   │   ├── direction_seq.pt        # BiLSTM for direction (PyTorch)
│   │   ├── seller_trap.pkl         # Trap risk model (sklearn)
│   │   ├── seller_regime.pkl       # Regime model (sklearn)
│   │   ├── seller_breach.pkl       # Breach probability model
│   │   ├── buyer_breakout.pkl      # Breakout detection
│   │   ├── buyer_spike.pkl         # Spike detection
│   │   └── buyer_theta.pkl         # Theta edge model
│   │
│   ├── 📂 data/                    # Market data (CSV)
│   │   ├── nifty_daily.csv         # Daily NIFTY close prices
│   │   └── vix_daily.csv           # Daily VIX values
│   │
│   └── requirements.txt            # Python dependencies
│
├── 📂 client/                      # Frontend: React + TypeScript
│   ├── src/
│   │   ├── components/             # React components
│   │   ├── pages/                  # Page components
│   │   ├── hooks/                  # Custom React hooks
│   │   ├── utils/                  # Utility functions
│   │   ├── App.tsx                 # Main app component
│   │   └── main.tsx                # Entry point
│   │
│   ├── public/                     # Static assets
│   └── package.json                # npm dependencies
│
├── 📂 server/                      # API server (optional)
│   └── ...                         # Server implementation
│
├── 📂 shared/                      # Shared code
│   └── ...                         # Shared utilities
│
├── config.py                       # Root config
├── infer.py                        # Root inference (uses aegismatrix-engine)
├── data_fetcher.py                 # Root data fetcher
├── train_all.py                    # Root training
├── test_api.py                     # Testing
├── schema.py                       # Root schema
│
├── vite.config.ts                  # Vite config
├── tsconfig.json                   # TypeScript config
├── tailwind.config.ts              # Tailwind CSS config
├── package.json                    # npm packages
├── drizzle.config.ts               # Database config
│
├── .github/workflows/              # GitHub Actions
│   └── inference.yml               # Inference schedule (every 30 min)
│   └── training.yml                # Training schedule (Saturdays)
│
└── README.md (original)            # Original documentation
```

---

## 📊 Code Statistics

### Overall Project Size

| Language | Files | Size (KB) |
|----------|-------|-----------|
| **Python** | 42 | 234.3 |
| **TypeScript** | 3,488 | 19,616.2 |
| **TypeScript React** | 203 | 520.0 |
| **JavaScript** | 9,041 | 113,272.9 |
| **Markdown** | 682 | 4,356.1 |
| **TOTAL** | 13,456 | 137,999.5 |

### Backend Breakdown (Python)

| Component | Files | Purpose |
|-----------|-------|---------|
| aegismatrix-engine/ | 25 | ML models, feature engineering, inference |
| Root Python | 5 | Config, data fetching, training, inference |
| **Total** | **42** | **234.3 KB** |

**Key Files:**
- `infer.py` - Main inference script (~200 lines)
- `train_all.py` - Training script (~150 lines)
- `data_fetcher.py` - Market data fetching (~180 lines)
- `config.py` - Configuration (~80 lines)

### Frontend Breakdown (TypeScript + React)

| Component | Files | Purpose |
|-----------|-------|---------|
| TypeScript | 3,488 | Core logic, types, utilities |
| React Components | 203 | UI components |
| **Total** | **3,691** | **20,136.2 KB** |

**Key Components:**
- Dashboard main page
- Market data visualization
- Direction predictions display
- Seller options analysis
- Buyer opportunities panel
- Real-time price ticker

### JavaScript (Node Dependencies)

- **9,041 files** (node_modules)
- **113,272.9 KB** (mostly dependencies)
- Includes: React, TypeScript, Vite, Tailwind, utilities, etc.

### Total Project Size: **138 MB**

---

## 🐍 Backend Setup

### Python Environment

**Python Version:** 3.12+

**Dependencies (requirements.txt):**
```
numpy==2.x           # Numerical computing
pandas==2.x          # Data manipulation
scikit-learn==1.x    # ML models
torch==2.x           # PyTorch for LSTM
yfinance==0.x        # Market data
joblib==1.x          # Model serialization
scipy==1.x           # Scientific computing
requests==2.x        # HTTP requests
```

### File Structure

```
aegismatrix-engine/
├── config.py              # Configuration
├── data_fetcher.py        # yfinance integration
├── infer.py              # Main inference
├── train_all.py          # Weekly training
├── schema.py             # Data schemas
│
├── direction/
│   ├── model.py          # BiLSTM architecture
│   └── today_direction.py # Same-day predictions
│
├── seller/
│   ├── model.py          # Trap, regime, breach models
│   └── features.py       # IV/RV percentiles, skew
│
├── buyer/
│   ├── model.py          # Breakout, spike, theta
│   └── features.py       # Momentum, gamma, theta
│
├── features/
│   ├── daily_features.py # Returns, volatility, technicals
│   └── intraday_features.py # Gamma, theta, momentum
│
├── models/               # Trained models
│   ├── direction_seq.pt  # PyTorch LSTM (~5 MB)
│   ├── seller_trap.pkl   # sklearn RandomForest (~1 MB)
│   ├── seller_regime.pkl # sklearn RandomForest (~1 MB)
│   ├── seller_breach.pkl # sklearn model (~1 MB)
│   ├── buyer_breakout.pkl
│   ├── buyer_spike.pkl
│   └── buyer_theta.pkl
│
├── data/                 # Market data
│   ├── nifty_daily.csv   # Daily closes (~50 KB)
│   └── vix_daily.csv     # Daily VIX (~40 KB)
│
└── requirements.txt      # Dependencies
```

### Running Backend

**Development:**
```bash
cd aegismatrix-engine

# Train models (weekly)
python train_all.py

# Run inference (daily/every 30 min)
python infer.py

# Test API
python test_api.py
```

**Output:**
- Creates: `../aegismatrix.json` with predictions
- Used by: Frontend dashboard

**Key Scripts:**

1. **data_fetcher.py** - Fetches market data
   - Downloads 5 years of NIFTY/VIX daily data
   - Gets live 1-min intraday bars
   - Saves to `data/` directory

2. **train_all.py** - Trains 7 ML models
   - Direction engine (BiLSTM on PyTorch)
   - Seller engine (trap, regime, breach)
   - Buyer engine (breakout, spike, theta)
   - Saves to `models/` directory

3. **infer.py** - Runs inference (main)
   - Loads trained models
   - Calculates 50+ features
   - Makes predictions
   - Outputs `aegismatrix.json`

---

## ⚛️ Frontend Setup

### Technology Stack

- **Framework:** React 18+
- **Language:** TypeScript
- **Bundler:** Vite
- **Styling:** Tailwind CSS
- **State:** Context API / React Hooks
- **HTTP:** axios or fetch

### File Structure

```
client/
├── src/
│   ├── components/         # Reusable components
│   │   ├── Header.tsx
│   │   ├── Dashboard.tsx
│   │   ├── PriceCard.tsx
│   │   ├── PredictionPanel.tsx
│   │   ├── SellerAnalysis.tsx
│   │   └── BuyerOpportunities.tsx
│   │
│   ├── pages/              # Page components
│   │   ├── Home.tsx
│   │   ├── Dashboard.tsx
│   │   └── Analysis.tsx
│   │
│   ├── hooks/              # Custom hooks
│   │   ├── useMarketData.ts
│   │   ├── usePredictions.ts
│   │   └── useRealtime.ts
│   │
│   ├── utils/              # Utilities
│   │   ├── api.ts          # API calls
│   │   ├── format.ts       # Data formatting
│   │   └── calculate.ts    # Calculations
│   │
│   ├── App.tsx             # Main app
│   ├── main.tsx            # Entry point
│   └── index.css           # Styles
│
├── public/                 # Static assets
│   ├── index.html
│   └── favicon.ico
│
├── package.json            # Dependencies
├── tsconfig.json           # TypeScript config
└── vite.config.ts          # Vite config
```

### Running Frontend

**Development:**
```bash
npm install
npm run dev
# Open http://localhost:5173
```

**Production:**
```bash
npm run build
npm run preview
```

**Key Features:**
- Real-time market data updates
- Direction predictions (1D/3D/Week)
- Option seller analysis
- Buyer opportunity detection
- Live price ticker
- Responsive design

---

## 📡 API Documentation

### Market Data Endpoint

**GET** `/api/market`
```json
{
  "generated_at": "2025-11-24T04:56:20.285396Z",
  "market": {
    "spot": 26068.15,
    "spot_change": -124.0,
    "spot_change_pct": -0.473,
    "vix": 12.899999618530273,
    "vix_change": -0.7300004959106445
  }
}
```

### Predictions Endpoint

**GET** `/api/predictions`
```json
{
  "direction": {
    "tomorrow": {"prediction": "UP", "confidence": 0.75},
    "next_3days": {"prediction": "DOWN", "confidence": 0.62},
    "week": {"prediction": "UP", "confidence": 0.68},
    "risk_score": 0.35
  },
  "seller": {
    "trap": {"score": 0.52, "label": "MEDIUM"},
    "expiry_stress": {"score": 0.34, "label": "CAUTION"},
    "safe_range": {"lower": 25900, "upper": 26200}
  },
  "buyer": {
    "breakout_today": {"score": 0.45, "label": "POTENTIAL"},
    "spike_bias": 0.62,
    "theta_edge": "POSITIVE"
  }
}
```

### Data Source: `aegismatrix.json`

Frontend reads this file generated by Python backend every 30 minutes.

---

## 📚 Training Pipeline

### Weekly Training (Saturday 00:00)

**Script:** `python train_all.py`

**Steps:**
1. Download 5 years of market data (yfinance)
2. Calculate 50+ technical features
3. Train Direction engine (BiLSTM)
4. Train Seller engine (trap, regime, breach)
5. Train Buyer engine (breakout, spike, theta)
6. Save 7 trained models to `models/`
7. Save model metadata & stats

**Time:** ~15-30 minutes

**Output:** 
- `models/direction_seq.pt` (~5 MB)
- `models/seller_*.pkl` (~3 MB)
- `models/buyer_*.pkl` (~3 MB)

**Features Calculated:**
- Direction: Returns, volatility, momentum, technicals
- Seller: IV, RV, skew, breach levels
- Buyer: Momentum, gamma, theta, intraday volatility

---

## 🔄 Inference Pipeline

### Every 30 Minutes (Mon-Fri 09:15-15:30)

**Script:** `python infer.py`

**Steps:**
1. Fetch live market data (1-min bars, daily close, VIX)
2. Build features from market data
3. Load trained models
4. Run predictions through models
5. Compute analysis metrics
6. Generate `aegismatrix.json`
7. Upload to repository/server

**Time:** ~30-60 seconds

**Output:** `aegismatrix.json` (~100 KB)
- Market data (spot, VIX, changes)
- Direction predictions (tomorrow, 3 days, week)
- Seller analysis (trap, stress, breach)
- Buyer signals (breakout, spike, theta)

**Key Functions:**

```python
# In infer.py
build_direction_features()    # Prepare data for direction model
build_seller_features()       # Prepare data for seller models
build_buyer_features()        # Prepare data for buyer models
predict_direction()           # Run BiLSTM predictions
compute_vol_trap_risk()       # ML: Volatility trap analysis
compute_expiry_stress()       # ML: Expiry stress calculation
compute_seller_flag()         # Summary for sellers
```

---

## 🤖 GitHub Actions Workflow

### Training Schedule

**File:** `.github/workflows/training.yml`

**Frequency:** Every Saturday at 00:00 UTC

```yaml
on:
  schedule:
    - cron: '0 0 * * 6'  # Saturday 00:00

jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt
      - run: python train_all.py
      - run: git add models/ && git commit -m "Weekly model training"
      - run: git push
```

### Inference Schedule

**File:** `.github/workflows/inference.yml`

**Frequency:** Every 30 minutes (Mon-Fri 09:15-15:30)

```yaml
on:
  schedule:
    - cron: '*/30 9-15 * * 1-5'  # Every 30 min weekdays

jobs:
  infer:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt
      - run: python infer.py
      - run: git add aegismatrix.json && git commit -m "Inference update"
      - run: git push
```

---

## 🐛 Troubleshooting

### Issue: Models fail to load

**Error:** `No module named 'numpy._core'`

**Solution:**
```bash
cd aegismatrix-engine
python train_all.py  # Retrain with current numpy
```

**Why:** Models pickled with numpy 1.x need retraining for 2.x compatibility.

### Issue: Inference doesn't run

**Check:**
```bash
python infer.py
# Look for error messages
# Check if aegismatrix.json was created
```

**Solutions:**
- Install dependencies: `pip install -r requirements.txt`
- Download data: `python data_fetcher.py`
- Check file permissions: `chmod 755 models/ data/`

### Issue: Frontend doesn't load data

**Check:**
```bash
npm run dev
# Open browser DevTools (F12)
# Check Network tab for 404 errors
```

**Solutions:**
- Verify `aegismatrix.json` exists
- Check file path in frontend code
- Ensure backend ran successfully

### Issue: Old values in dashboard

**Solution:**
- Check timestamp in JSON (should be recent)
- Verify inference ran: `ls -la aegismatrix.json`
- Check for errors in `infer.py` output

---

## ❓ FAQ

### Q: How often does the dashboard update?

**A:** Every 30 minutes during market hours (Mon-Fri 09:15-15:30).

### Q: Can I run inference manually?

**A:** Yes! Just run:
```bash
cd aegismatrix-engine
python infer.py
```

### Q: How do I retrain models?

**A:** Run:
```bash
cd aegismatrix-engine
python train_all.py
```

### Q: How much historical data is used?

**A:** 
- Training: 5 years of daily data
- Inference: Latest market data + intraday bars

### Q: Can I change prediction horizons?

**A:** Yes, edit `config.py`:
```python
DIRECTION_HORIZONS = ["t1", "t3", "t5"]  # Tomorrow, 3-days, week
```

### Q: What markets does it cover?

**A:** Currently NIFTY50 index (India). Can extend to other instruments.

### Q: How accurate are predictions?

**A:** Varies by horizon and market regime. Check backtests in training logs.

### Q: Can I deploy this to production?

**A:** Yes! Deploy both backend (Python) and frontend (React). Ensure:
- Environment variables configured
- Database setup (if using)
- Scheduled jobs configured
- Error monitoring setup

### Q: What's the performance impact?

**A:** 
- Training: ~15-30 minutes (weekly)
- Inference: ~30-60 seconds (every 30 min)
- Dashboard load: <2 seconds

### Q: Can I add more features?

**A:** Yes! Edit feature engineering functions:
- `features/daily_features.py`
- `features/intraday_features.py`

Then retrain models.

---

## 📞 Support

### Getting Help

1. **Check logs:**
   ```bash
   # Python backend
   python infer.py 2>&1 | tee inference.log
   
   # GitHub Actions
   # Check Actions tab in repository
   ```

2. **Read documentation files:**
   - `SOLUTION_SUMMARY.md` - Issue explanation
   - `FIX_CHECKLIST.md` - Fix procedures
   - `COMPLETE_DIAGNOSIS.md` - Technical details

3. **Common fixes:**
   ```bash
   # Update dependencies
   pip install -r requirements.txt --upgrade
   
   # Clear cache and retrain
   rm -rf models/
   python train_all.py
   
   # Download fresh data
   python data_fetcher.py
   ```

---

## 📝 Summary

| Aspect | Details |
|--------|---------|
| **Language** | Python (backend), TypeScript/React (frontend) |
| **Backend Size** | 234.3 KB (42 files) |
| **Frontend Size** | 20,136.2 KB (3,691 files) |
| **Total Project** | 138 MB |
| **Update Frequency** | Every 30 minutes |
| **Training Frequency** | Weekly (Saturdays) |
| **Prediction Horizons** | 1-day, 3-day, 1-week |
| **Models** | 7 (1 Direction, 3 Seller, 3 Buyer) |
| **Features** | 50+ technical indicators |
| **Status** | ✅ Fully Operational |

---

## ✅ Status Check

**Current Status:** 🟢 **FULLY OPERATIONAL**

- ✅ Spot price: Updating live
- ✅ VIX: Updating live
- ✅ Direction predictions: Dynamic
- ✅ Volatility Trap: Dynamic (after fix)
- ✅ Expiry Stress: Dynamic (after fix)
- ✅ Buyer signals: Dynamic
- ✅ Dashboard: Real-time
- ✅ GitHub Actions: Running

**Last Fixed:** November 24, 2025 (numpy compatibility issue resolved)

---

**Happy Trading! 🚀📈**
