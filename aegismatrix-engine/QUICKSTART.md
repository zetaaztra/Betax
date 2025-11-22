# Quick Start Guide - AegisMatrix

## ⚡ 5-Minute Overview

AegisMatrix is a three-engine quant system for NIFTY options:

- **Direction Engine**: Predicts directional bias over 6 time horizons
- **Seller Engine**: Risk metrics for short strategies (safe range, trap risk, breach probabilities)
- **Buyer Engine**: Volatility & spike analytics for long strategies (breakout, gamma windows, theta edge)

**Everything flows into one JSON file** → `client/public/data/aegismatrix.json`

---

## 🏗️ Current State

✅ **Complete skeleton** with:
- Full directory structure
- All Python engine files (placeholder heuristics)
- Frontend stubs ready for data binding
- GitHub Actions CI/CD pipeline
- Pydantic schema validation
- TypeScript data types

🟡 **Needs implementation:**
- Real ML models (train locally, save to `aegismatrix-engine/models/`)
- Frontend tiles connected to JSON data
- Optional: database for historical analysis

---

## 🚀 Getting Started

### Step 1: Test Python Engine Locally

```bash
cd aegis-dashboard
cd aegismatrix-engine

# Install dependencies
pip install -r requirements.txt

# Run inference (generates JSON)
python infer.py

# Check output
cat ../client/public/data/aegismatrix.json
```

Expected: A valid `aegismatrix.json` in `client/public/data/` with market, direction, seller, buyer blocks.

### Step 2: Test Frontend

```bash
cd aegis-dashboard/client

# Install dependencies
npm install

# Start dev server
npm run dev

# or build for production
npm run build
```

Navigate to tabs and verify structure renders (data binding to come).

### Step 3: Understand the JSON

Open `client/public/data/aegismatrix.json` and explore:

```json
{
  "generated_at": "2025-11-21T04:50:00Z",
  "market": { "spot": 19783.45, "regime": "LOW_VOL_BULL", ... },
  "direction": {
    "today": { "direction": "UP", "conviction": 0.68, ... },
    "horizons": { "t1": {...}, "t3": {...}, ... },
    "risk_score": 0.37
  },
  "seller": {
    "safe_range": { "lower": 19500, "upper": 20050 },
    "trap": { "score": 0.64, "label": "HIGH" },
    ...
  },
  "buyer": {
    "breakout_today": { "score": 0.78, "label": "HIGH" },
    ...
  }
}
```

---

## 🤖 Training Models (Next Phase)

Once you have training data and backtesting validation:

```bash
cd aegismatrix-engine

# Train direction model
python direction/train_direction.py
# → Saves to models/direction_seq.pt, models/direction_magnitude.pkl

# Train seller model
python seller/train_seller.py
# → Saves to models/seller_*.pkl

# Train buyer model
python buyer/train_buyer.py
# → Saves to models/buyer_*.pt / .pkl
```

Then update engine files to **load and use** trained models:

```python
# direction/model.py
def load_models():
    import joblib
    import torch
    
    dir_seq = torch.load("../models/direction_seq.pt")
    mag_model = joblib.load("../models/direction_magnitude.pkl")
    return dir_seq, mag_model
```

---

## 🔗 Connecting Frontend to JSON

Currently, tabs are **stubs**. To bind data:

```typescript
// client/src/components/tabs/direction-tab.tsx

import { loadAegisMatrixData } from '@/lib/aegis-data';

export function DirectionTab() {
  const [data, setData] = useState<AegisMatrixData | null>(null);
  
  useEffect(() => {
    loadAegisMatrixData().then(setData);
  }, []);
  
  if (!data) return <div>Loading...</div>;
  
  return (
    <div>
      <TodayDirectionTile data={data.direction.today} />
      {Object.entries(data.direction.horizons).map(([key, horizon]) => (
        <HorizonTile key={key} horizon={horizon} />
      ))}
      <RiskScoreDial score={data.direction.risk_score} />
    </div>
  );
}
```

---

## 📋 Checklist for Going Live

- [ ] Train all three models locally (direction, seller, buyer)
- [ ] Save models to `aegismatrix-engine/models/`
- [ ] Update `direction/model.py`, `seller/model.py`, `buyer/model.py` to load trained models
- [ ] Test `python infer.py` locally with real data
- [ ] Verify JSON structure with `schema.py` validation
- [ ] Connect frontend tabs to JSON data (use `aegis-data.ts`)
- [ ] Build frontend: `npm run build`
- [ ] Configure GitHub Actions secrets:
  - `CLOUDFLARE_API_TOKEN`
  - `CLOUDFLARE_ACCOUNT_ID`
- [ ] Push to GitHub → CI/CD runs automatically
- [ ] Monitor CI/CD runs and logs
- [ ] Verify Cloudflare Pages deployment

---

## 📁 Key Files to Edit

| File | Purpose |
|------|---------|
| `aegismatrix-engine/direction/model.py` | Load trained direction model |
| `aegismatrix-engine/seller/model.py` | Load trained seller model |
| `aegismatrix-engine/buyer/model.py` | Load trained buyer model |
| `client/src/components/tabs/direction-tab.tsx` | Render direction data |
| `client/src/components/tabs/seller-tab.tsx` | Render seller data |
| `client/src/components/tabs/buyer-tab.tsx` | Render buyer data |

---

## 🔍 How Data Flows

```
GitHub Actions (every 30 min)
    ↓
infer.py
    ├─ Fetch yfinance data
    ├─ Build features
    ├─ Run 3 engines
    ├─ Validate JSON with Pydantic
    └─ Write aegismatrix.json
        ↓
    Vite build
        ↓
    Deploy to Cloudflare Pages
        ↓
    Browser: React loads JSON → renders tabs
```

---

## 📚 Documentation

- **`AEGISMATRIX_STRUCTURE.md`**: Complete architecture (formulas, algorithms, data flow)
- **`PROJECT_STRUCTURE_VISUAL.md`**: Visual directory tree + engine explanations
- **`RESTRUCTURE_COMPLETE.txt`**: Summary of what was created

---

## 🤔 Common Questions

### Q: Can I run the backend without GitHub Actions?

**A:** Yes! Run locally:
```bash
cd aegismatrix-engine
python infer.py
```
This generates `client/public/data/aegismatrix.json` immediately.

### Q: What data sources are used?

**A:** Currently yfinance (NIFTY: `^NSEI`, VIX: `^INDIAVIX`). ~15–30 min delay. Designed for structural signals, not tick trading.

### Q: Can I deploy without training models?

**A:** Yes! The skeleton uses placeholder heuristics. You can deploy now to verify the pipeline works. Replace with trained models later.

### Q: How often is the JSON regenerated?

**A:** Every 30 minutes during Indian market hours (UTC 03:45–10:00, Mon–Fri) by GitHub Actions.

### Q: Is this production-ready?

**A:** The architecture and infrastructure are ready. The models are placeholders. Before trading, validate each engine on historical data.

---

## 🚨 Important Notes

1. **No trade recommendations**: This is decision support, not trading advice.
2. **Models are critical**: Garbage in = garbage out. Invest heavily in training & backtesting.
3. **Regulatory**: If you're building for clients/fund, ensure compliance with local regulations.
4. **Static frontend**: The JSON is read-only from the browser. No live updates via API.

---

## 📞 Next Steps

1. **Test locally** → `python infer.py`
2. **Train models** → `direction/train_direction.py` etc.
3. **Build frontend** → `npm run build`
4. **Setup Cloudflare** → Add secrets to GitHub
5. **Deploy** → Push to GitHub → CI/CD handles rest

---

**Questions?** Refer to `AEGISMATRIX_STRUCTURE.md` for deep dive on each engine.

Happy trading! 🚀
