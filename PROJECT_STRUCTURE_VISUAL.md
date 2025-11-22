# AegisMatrix Project Structure - Complete Summary

## 📊 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        GITHUB ACTIONS                            │
│                   (Every 30 min, Mon-Fri)                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    aegismatrix-engine/                           │
│                   (Python ML Backend)                            │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ infer.py (MAIN)                                          │  │
│  │  └─ Fetches: NIFTY + VIX daily & intraday               │  │
│  │  └─ Builds: 3 feature matrices                          │  │
│  │  └─ Runs: 3 engines                                     │  │
│  │  └─ Outputs: aegismatrix.json                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌─────────────────┬──────────────────┬──────────────────┐      │
│  │  direction/     │   seller/        │    buyer/        │      │
│  │                 │                  │                  │      │
│  │  • model.py     │ • model.py       │ • model.py       │      │
│  │  • today_dir.py │ • (8 functions)  │ • (7 functions)  │      │
│  │  • (2 models)   │                  │                  │      │
│  └─────────────────┴──────────────────┴──────────────────┘      │
│                                                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼ JSON output
        ┌────────────────────────────────┐
        │  client/public/data/           │
        │  aegismatrix.json (static)     │
        └────────────────────┬───────────┘
                             │
                             ▼
        ┌────────────────────────────────┐
        │   React Frontend (Vite)         │
        │   client/src/App.tsx            │
        │                                 │
        │  ┌──────┬──────────┬──────────┐ │
        │  │ Dir  │ Sellers  │ Buyers   │ │
        │  │ Tab  │ Tab      │ Tab      │ │
        │  └──────┴──────────┴──────────┘ │
        │                                 │
        └────────────────────┬────────────┘
                             │
                             ▼
        ┌────────────────────────────────┐
        │  Cloudflare Pages (Static CDN)  │
        │  → Public read-only             │
        └────────────────────────────────┘
```

## 📁 Full Directory Tree

```
aegis-dashboard/
│
├── 📂 aegismatrix-engine/              ⭐ NEW: Python ML Backend
│   ├── config.py                       📌 Central config (paths, symbols, horizons)
│   ├── data_fetcher.py                 📌 yfinance wrapper (no caching yet)
│   ├── schema.py                       📌 Pydantic validation (ALL blocks)
│   ├── infer.py                        🔥 MAIN: orchestrates 3 engines → JSON
│   ├── requirements.txt                📌 pandas, numpy, yfinance, pydantic, scipy
│   │
│   ├── 📂 config/                      (placeholder for future configs)
│   │
│   ├── 📂 features/
│   │   ├── daily_features.py           📌 Build feature matrices (60-day lookback)
│   │   └── intraday_features.py        📌 Gap, ORB, gamma windows (5m data)
│   │
│   ├── 📂 direction/                   ⭐ Engine 1: Directional Forecasts
│   │   ├── model.py                    📌 Load models, predict horizons (t1-t40)
│   │   ├── today_direction.py          📌 Combine daily + intraday → today's call
│   │   └── train_direction.py          (local training, not in CI/CD)
│   │
│   ├── 📂 seller/                      ⭐ Engine 2: Option Sellers (RangeShield)
│   │   ├── model.py                    📌 safe_range, trap, skew, breach, flag
│   │   └── train_seller.py             (local training, not in CI/CD)
│   │
│   ├── 📂 buyer/                       ⭐ Engine 3: Option Buyers (PulseWave)
│   │   ├── model.py                    📌 breakout, spike, gamma, theta, env
│   │   └── train_buyer.py              (local training, not in CI/CD)
│   │
│   ├── 📂 models/                      🔐 Saved model binaries
│   │   ├── direction_seq.pt            (BiLSTM + Attention)
│   │   ├── direction_magnitude.pkl     (XGBoost)
│   │   ├── seller_regime.pkl
│   │   ├── buyer_breakout.pt
│   │   └── ...
│   │
│   └── 📂 data/
│       ├── raw/                        (yfinance downloads)
│       ├── processed/                  (feature-engineered)
│       └── intraday/                   (5m candle cache)
│
├── 📂 client/                          React Frontend (Vite)
│   ├── index.html
│   ├── 📂 public/
│   │   └── 📂 data/
│   │       └── aegismatrix.json        🔥 GENERATED by Python (read-only)
│   │
│   └── 📂 src/
│       ├── App.tsx
│       ├── main.tsx
│       ├── index.css
│       │
│       ├── 📂 components/
│       │   ├── concentric-background.tsx
│       │   ├── cookie-consent-modal.tsx
│       │   ├── disclaimer-modal.tsx
│       │   ├── footer.tsx
│       │   ├── how-to-use.tsx
│       │   ├── theme-provider.tsx
│       │   ├── tile-help-modal.tsx
│       │   │
│       │   ├── 📂 tabs/                ⭐ NEW: Tab Containers
│       │   │   ├── direction-tab.tsx   📌 Today, horizons, risk score
│       │   │   ├── seller-tab.tsx      📌 Safe range, trap, skew, breach, flag
│       │   │   └── buyer-tab.tsx       📌 Breakout, spike, gamma, theta, env
│       │   │
│       │   ├── 📂 tiles/               🔄 REORGANIZED by Engine
│       │   │   ├── 📂 direction/
│       │   │   │   ├── today-direction.tsx
│       │   │   │   ├── horizon-tile.tsx
│       │   │   │   ├── spot-tile.tsx
│       │   │   │   ├── vix-tile.tsx
│       │   │   │   ├── direction-risk.tsx
│       │   │   │   └── market-regime-tile.tsx
│       │   │   │
│       │   │   ├── 📂 seller/
│       │   │   │   ├── safe-range-tile.tsx
│       │   │   │   ├── max-pain-tile.tsx
│       │   │   │   ├── expiry-stress-tile.tsx
│       │   │   │   ├── vol-trap-tile.tsx
│       │   │   │   ├── skew-pressure-tile.tsx
│       │   │   │   ├── breach-curve.tsx
│       │   │   │   ├── seller-flag-tile.tsx
│       │   │   │   └── ...
│       │   │   │
│       │   │   ├── 📂 buyer/
│       │   │   │   ├── breakout-gauge.tsx
│       │   │   │   ├── breakout-horizon-map.tsx
│       │   │   │   ├── spike-direction-bias.tsx
│       │   │   │   ├── gamma-windows.tsx
│       │   │   │   ├── theta-edge-tile.tsx
│       │   │   │   ├── buyer-environment.tsx
│       │   │   │   └── ...
│       │   │   │
│       │   │   └── 📂 shared/          ⭐ NEW: Shared Components
│       │   │       ├── shared-tiles.tsx 📌 RiskScoreDial, MiniSparkline, ProbabilityCurve
│       │   │
│       │   └── 📂 ui/                  Shadcn UI (unchanged)
│       │       ├── button.tsx
│       │       ├── card.tsx
│       │       ├── dialog.tsx
│       │       ├── dropdown-menu.tsx
│       │       ├── form.tsx
│       │       └── ...
│       │
│       ├── 📂 hooks/
│       │   ├── use-mobile.tsx
│       │   └── use-toast.ts
│       │
│       ├── 📂 lib/
│       │   ├── queryClient.ts
│       │   ├── utils.ts
│       │   └── aegis-data.ts           ⭐ NEW: Load aegismatrix.json
│       │
│       └── 📂 pages/
│           ├── about.tsx
│           ├── buyer-view.tsx
│           ├── dashboard.tsx           (Tab layout wrapper)
│           ├── seller-view.tsx
│           ├── privacy.tsx
│           ├── terms.tsx
│           └── ...
│
├── 📂 server/                          Express Backend (optional)
│   ├── index.ts
│   ├── routes.ts
│   ├── storage.ts
│   └── vite.ts
│
├── 📂 shared/
│   └── schema.ts                       TypeScript types
│
├── 📂 .github/
│   └── 📂 workflows/
│       └── aegismatrix-infer-build.yml ⭐ NEW: CI/CD Pipeline
│
├── package.json
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.ts
├── postcss.config.js
├── drizzle.config.ts
├── components.json
│
├── 📄 AEGISMATRIX_STRUCTURE.md         Complete architecture guide
├── 📄 RESTRUCTURE_COMPLETE.txt         This summary
└── 📂 attached_assets/
```

## 🔥 Three Engines Explained

### Direction Engine (AegisCore)
**Input:** Daily NIFTY & VIX (5 years)  
**Output:** Direction forecasts for 6 horizons + today's intraday call + risk score

```
Horizons: t1 (tomorrow), t3, t5, t10, t20, t40 (days ahead)
For each: { direction: UP/DOWN/NEUTRAL, expected_move_points: float, conviction: 0-1 }
Today:    { direction, expected_move_points, conviction, intraday_vol_score }
Risk:     0-1 (higher = less confident in forecast)
```

### Seller Engine (RangeShield)
**Input:** Daily features + volatility metrics  
**Output:** Range bands, risk scores, probabilities for short strategies

```
safe_range:         { lower, upper } for next 30 days
max_pain:           { lower, upper, confidence }
trap:               { score 0-1, label LOW/MED/HIGH, iv_pct, rv_pct }
skew:               { put_skew, call_skew, net_skew } (-1 to +1)
expiry_stress:      { score 0-1, label CALM/CAUTION/HOSTILE }
breach_probs:       [{ distance: 100, prob: 0.18 }, ...]
seller_flag:        { label: FAVOURABLE/CAUTION/HOSTILE, color, reasons }
```

### Buyer Engine (PulseWave)
**Input:** Daily features + intraday 5m candles  
**Output:** Breakout potential, spike direction, volatility windows for long strategies

```
breakout_today:     { score 0-1, label LOW/MED/HIGH }
breakout_next:      [{ day_offset: 1-5, score, label }, ...]
spike_direction:    { up_prob, down_prob }
gamma_windows:      [{ window: "09:45-10:15", score }, ...]
theta_edge:         { score 0-1, label DONT_WASTE/BORDERLINE/EDGE_JUSTIFIES }
regime:             TREND_FOLLOWING / MEAN_REVERT / CHOPPY
buyer_environment:  { label: PREMIUM_FRIENDLY/SPECULATIVE/UNFAVOURABLE, color, reasons }
```

## 📊 JSON Output Structure

```json
{
  "generated_at": "2025-11-21T04:50:00Z",
  
  "market": {
    "spot": 19783.45,
    "spot_change": 45.2,
    "spot_change_pct": 0.0023,
    "vix": 15.4,
    "vix_change": -0.8,
    "vix_change_pct": -0.049,
    "regime": "LOW_VOL_BULL"
  },
  
  "direction": {
    "today": { "direction": "UP", "expected_move_points": 65.0, ... },
    "horizons": {
      "t1": { "label": "Tomorrow", "direction": "UP", ... },
      "t3": { "label": "Next 3 Days", "direction": "UP", ... },
      ...
    },
    "risk_score": 0.37
  },
  
  "seller": {
    "safe_range": { "lower": 19500.0, "upper": 20050.0, ... },
    "max_pain": { "lower": 19800.0, "upper": 19950.0, ... },
    "trap": { "score": 0.64, "label": "HIGH", ... },
    "skew": { "put_skew": 0.35, "call_skew": 0.12, ... },
    "expiry_stress": { "score": 0.72, "label": "HOSTILE" },
    "breach_probabilities": [{ "distance": 100, "probability": 0.18 }, ...],
    "seller_flag": { "label": "CAUTION", "color": "AMBER", "reasons": [...] }
  },
  
  "buyer": {
    "breakout_today": { "score": 0.78, "label": "HIGH" },
    "breakout_next": [{ "day_offset": 1, "score": 0.65, ... }, ...],
    "spike_direction_bias": { "up_prob": 0.7, "down_prob": 0.3 },
    "gamma_windows": [{ "window": "09:45-10:15", "score": 0.82 }, ...],
    "theta_edge": { "score": 0.61, "label": "EDGE_JUSTIFIES_PREMIUM" },
    "regime": "TREND_FOLLOWING",
    "buyer_environment": { "label": "PREMIUM_FRIENDLY", "color": "GREEN", ... }
  }
}
```

## 🚀 CI/CD Workflow

**Trigger:** Every 30 minutes during market hours (UTC 03:45–10:00, Mon–Fri)

**Steps:**
1. Checkout code
2. Setup Python 3.11
3. Install aegismatrix-engine deps
4. Run `python infer.py` → generates JSON
5. Setup Node.js 20
6. Install npm deps
7. Build Vite (`npm run build`)
8. Deploy to Cloudflare Pages (static)

## ✅ Status

| Component | Status | Notes |
|-----------|--------|-------|
| Directory structure | ✅ Complete | All folders created |
| Python engine | ✅ Stubbed | Placeholder heuristics, ready for real models |
| Feature engineering | ✅ Stubbed | daily_features.py, intraday_features.py ready |
| Direction engine | ✅ Stubbed | Horizons, today direction, risk score |
| Seller engine | ✅ Stubbed | 8 functions, all metrics included |
| Buyer engine | ✅ Stubbed | 7 functions, all metrics included |
| infer.py | ✅ Complete | Orchestrates all 3 engines |
| schema.py | ✅ Complete | Pydantic validation for every block |
| Frontend tabs | ✅ Stubbed | direction-tab, seller-tab, buyer-tab |
| aegis-data.ts | ✅ Complete | Data loader + TypeScript types |
| GitHub Actions | ✅ Complete | CI/CD pipeline ready |
| Documentation | ✅ Complete | AEGISMATRIX_STRUCTURE.md |

## 🎯 To Go Live

1. **Train models locally:**
   ```bash
   cd aegismatrix-engine
   python direction/train_direction.py
   python seller/train_seller.py
   python buyer/train_buyer.py
   ```

2. **Update engine files to load trained models**

3. **Test locally:**
   ```bash
   python infer.py
   # Check client/public/data/aegismatrix.json
   ```

4. **Configure GitHub Actions secrets:**
   - `CLOUDFLARE_API_TOKEN`
   - `CLOUDFLARE_ACCOUNT_ID`

5. **Push to GitHub → CI/CD deploys automatically**

---

**All skeleton code is in place. This is production-ready to deploy placeholder models; replace with trained ML later.**
