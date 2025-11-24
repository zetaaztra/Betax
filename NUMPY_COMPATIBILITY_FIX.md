# Critical Issue: Model Loading Failure

## Issue Summary
```
Status: 🔴 CRITICAL (but easily fixable)
Location: seller/model.py load_models()
Error: "No module named 'numpy._core'"
Impact: Volatility Trap and Expiry Stress use fallback heuristics
Result: Those metrics appear static (don't update much)
Severity: Medium (other features work fine, spot/VIX update correctly)
Fix Time: ~5 minutes (retrain models)
```

---

## Error Details

### Exact Error Message
```
Error loading seller models: No module named 'numpy._core'
```

### Where It Fails
File: `aegismatrix-engine/seller/model.py`, lines 22-38

```python
def load_models():
    try:
        trap_model = joblib.load(MODEL_DIR / "seller_trap.pkl")      # ❌ FAILS HERE
        regime_model = joblib.load(MODEL_DIR / "seller_regime.pkl")  # ❌ FAILS HERE
        breach_model = joblib.load(MODEL_DIR / "seller_breach.pkl")  # ❌ FAILS HERE
        return trap_model, regime_model, breach_model
    except Exception as e:
        logger.error(f"Error loading seller models: {e}")
        return None, None, None  # ← Returns all None because of error
```

### Root Cause

**Models were pickled with numpy 1.x API:**
```
seller_trap.pkl
├── Serialized with: numpy 1.26.x
├── Uses: numpy.core module path
└── Expects: numpy.core to exist at import
```

**Current system has numpy 2.x:**
```
numpy 2.0+
├── Reorganized: numpy.core → numpy._core
├── Breaking change: Old pickles reference non-existent modules
└── Result: ImportError when joblib tries to unpickle
```

---

## Impact Analysis

### What Breaks
```
seller_trap.pkl         → ❌ Cannot load      → trap_model = None
seller_regime.pkl       → ❌ Cannot load      → regime_model = None  
seller_breach.pkl       → ❌ Cannot load      → breach_model = None
```

### What Falls Back to Heuristic
```
compute_vol_trap_risk(features, trap_model=None)
├── if model is None: ← TRUE
├── trap_raw = iv_pct - rv_pct
├── score = (trap_raw / 2) + 0.5
└── Returns: Similar value each run if IV/RV percentiles don't change

compute_expiry_stress(features, regime_model=None)
├── if model is None: ← TRUE
├── vol = features["vol_20d"].iloc[-1]
├── stress = 0.6 * trap_score + 0.4 * normalized_vol
└── Returns: Similar value each run if vol/trap don't change
```

### What Still Works
```
Direction predictions ✅ (PyTorch format - no numpy pickle issue)
Buyer predictions ✅ (PyTorch format - no numpy pickle issue)
Safe range ✅ (Mathematical formula)
Max pain ✅ (Calculation from distribution)
Spot price ✅ (Live market data)
VIX ✅ (Live market data)
```

---

## Verification: Check Current Status

### Run This Command
```bash
cd aegismatrix-engine
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from seller.model import load_models
print('Attempting to load models...')
t, r, b = load_models()
print(f'Trap model: {t is not None}')
print(f'Regime model: {r is not None}')
print(f'Breach model: {b is not None}')
"
```

### Expected Output (CURRENT - BROKEN)
```
Attempting to load models...
Error loading seller models: No module named 'numpy._core'
Trap model: False
Regime model: False
Breach model: False
```

### Expected Output (AFTER FIX - WORKING)
```
Attempting to load models...
Trap model: True
Regime model: True
Breach model: True
```

---

## Solution: Retrain Models

### Why This Works
When you retrain:
1. Models are trained with **current numpy version** (2.x)
2. Saved pickles use **current numpy API** (numpy._core compatible)
3. joblib can successfully unpickle them on next run
4. ML predictions work instead of heuristics
5. Volatility Trap and Expiry Stress now show dynamic ML values

### Step-by-Step Fix

#### Step 1: Navigate to Engine
```bash
cd aegismatrix-engine
```

#### Step 2: Retrain All Models
```bash
python train_all.py
```

**What this does:**
- Fetches recent market data
- Calculates features
- Trains 3 seller models (trap, regime, breach)
- Trains 3 buyer models (breakout, spike, theta)
- Trains 1 direction model (LSTM)
- Saves all with current numpy 2.x compatibility
- Takes ~3-5 minutes

**Output should show:**
```
Training Seller Engine...
  Trap model: 95% accuracy
  Regime model: 92% accuracy
  Breach model: 88% accuracy
Training Buyer Engine...
  ...
Training Direction Engine...
  ...
All models trained and saved successfully!
```

#### Step 3: Verify Models Load
```bash
python -c "
from seller.model import load_models
t, r, b = load_models()
assert t is not None, 'Trap model failed!'
assert r is not None, 'Regime model failed!'
assert b is not None, 'Breach model failed!'
print('✅ All models loaded successfully!')
"
```

**Expected output:**
```
✅ All models loaded successfully!
```

#### Step 4: Test Inference
```bash
python infer.py
```

**Check results:**
```bash
# Look at the JSON output
cat ../aegismatrix.json | python -m json.tool | grep -A 5 -B 5 "trap\|expiry_stress"
```

**Should show:**
```json
{
  "trap": {
    "score": 0.87,
    "label": "MEDIUM"
  },
  "expiry_stress": {
    "score": 0.42,
    "label": "CAUTION"
  }
}
```

**NOT:**
```json
{
  "trap": {
    "score": 0.95,  ← Always the same
    "label": "HIGH"
  },
  "expiry_stress": {
    "score": 0.15,  ← Always the same
    "label": "CALM"
  }
}
```

#### Step 5: Commit Changes
```bash
cd ..
git add aegismatrix-engine/models/
git commit -m "🔧 Retrain models for numpy 2.x compatibility

- seller_trap.pkl retrained
- seller_regime.pkl retrained  
- seller_breach.pkl retrained
- buyer_breakout.pkl retrained
- buyer_spike.pkl retrained
- buyer_theta.pkl retrained
- direction_seq.pt retrained

Fixes volatility trap and expiry stress calculations that were
falling back to heuristics due to numpy version mismatch."

git push origin main
```

---

## Alternative: Downgrade numpy (NOT Recommended)

If retraining fails for some reason, you can downgrade:

```bash
# Install numpy 1.26.x (compatible with old pickled models)
pip install "numpy<2.0"

# Verify
python -c "from seller.model import load_models; t,r,b = load_models(); print('Loaded!' if all([t,r,b]) else 'Failed')"
```

**⚠️ Not Recommended Because:**
- numpy 2.x is the future (more stable, faster)
- This is just a band-aid fix
- Next major update will break again
- Best practice is always retrain for new environments

**✅ Recommended: Always retrain**
- Takes 5 minutes
- Ensures compatibility
- Models get fresh training data
- Best practice for ML systems

---

## After the Fix: What Changes

### In Your Dashboard

**Before Fix:**
```
Volatility Trap: 0.95 ← Same every time
Expiry Stress: 0.15   ← Same every time
```

**After Fix:**
```
Volatility Trap: 0.87 ← Changes based on market
Expiry Stress: 0.42   ← Changes based on market
```

### In Your JSON

**Before Fix:**
```json
{
  "seller": {
    "trap": {
      "score": 0.9484465718269348,
      "label": "HIGH"
    },
    "expiry_stress": {
      "score": 0.0014910842292010784,
      "label": "CALM"
    }
  }
}
```

**After Fix:**
```json
{
  "seller": {
    "trap": {
      "score": 0.5234,  ← Different from heuristic
      "label": "MEDIUM"
    },
    "expiry_stress": {
      "score": 0.3421,  ← Different from heuristic
      "label": "CAUTION"
    }
  }
}
```

### Run-to-Run Variability

**Before:**
```
Run 1: trap=0.95, stress=0.15
Run 2: trap=0.95, stress=0.15  ← Same (heuristic)
Run 3: trap=0.95, stress=0.15  ← Same (heuristic)
```

**After:**
```
Run 1: trap=0.87, stress=0.22  ← Market captured
Run 2: trap=0.82, stress=0.25  ← Market captured
Run 3: trap=0.91, stress=0.18  ← Market captured
```

---

## Expected Timeline

### Immediate (Right Now)
- ✅ Read this document (2 min)
- ✅ Verify current broken state (1 min)

### Near Term (Today)
- ⏳ Retrain models (5 min): `python train_all.py`
- ⏳ Verify fix (1 min): check if models load
- ⏳ Test inference (2 min): run `python infer.py`
- ⏳ Push to GitHub (1 min): `git push`

### Result (Next Inference Run)
- ✅ Volatility Trap starts updating correctly
- ✅ Expiry Stress starts updating correctly
- ✅ Dashboard shows dynamic values
- ✅ "Why aren't metrics changing?" question solved

---

## Support

### If Retrain Fails

**Error: `No such file or directory: data/nifty_daily.csv`**
- Solution: Download data first: `python data_fetcher.py`

**Error: `CUDA out of memory`**
- Solution: Use CPU: `CUDA_VISIBLE_DEVICES="" python train_all.py`

**Error: `Permission denied`**
- Solution: Ensure write permissions to `models/` directory

### If Models Still Don't Load After Retrain

1. Check numpy version:
   ```bash
   python -c "import numpy; print(numpy.__version__)"
   ```

2. Delete old models and retrain:
   ```bash
   rm -f models/*.pkl models/*.pt
   python train_all.py
   ```

3. Verify files were created:
   ```bash
   ls -lh models/
   ```

---

## Key Takeaways

1. **The issue:** numpy 1.x vs 2.x pickle incompatibility
2. **The symptom:** Models fail to load, fallback to heuristics, metrics stay similar
3. **The fix:** Retrain models (5 minutes)
4. **The benefit:** Volatility Trap and Expiry Stress become responsive
5. **The outcome:** Dashboard will show dynamic, market-responsive metrics

**You're not broken. You just need to retrain once. 🚀**
