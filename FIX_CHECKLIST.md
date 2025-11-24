# ✅ Fix Checklist - Model Loading Numpy Compatibility Issue

## 🎯 The Issue
Models fail to load: `Error: No module named 'numpy._core'`
Result: Volatility Trap and Expiry Stress use fallback heuristics
Status: 🟡 Fixable in 5 minutes

---

## 📋 Pre-Fix Checklist

- [ ] Read [DIAGNOSIS_SUMMARY.md](./DIAGNOSIS_SUMMARY.md) (2 min) ← Start here
- [ ] Understood that models incompatible with numpy 2.x
- [ ] Know why metrics appear static (heuristic fallback)
- [ ] Know that the fix is simply retraining
- [ ] Have access to terminal/command line
- [ ] Have write permissions to `aegismatrix-engine/models/`

---

## 🔧 Fix Execution Checklist

### Phase 1: Prepare
- [ ] Open terminal/command prompt
- [ ] Navigate to project: `cd aegismatrix-engine`
- [ ] Verify you're in correct directory:
  ```bash
  # Should show model files
  ls models/
  # Should show: seller_trap.pkl, seller_regime.pkl, etc.
  ```
- [ ] Check current numpy version (optional):
  ```bash
  python -c "import numpy; print(numpy.__version__)"
  # Should be 2.x
  ```

### Phase 2: Verify Current Broken State
- [ ] Check if models load (optional):
  ```bash
  python -c "
  from seller.model import load_models
  t, r, b = load_models()
  print(f'Models loaded: {t is not None and r is not None}')
  "
  # Should show: Models loaded: False
  ```

### Phase 3: Retrain Models (THE FIX)
- [ ] Run: `python train_all.py`
  - ⏱️ Takes 3-5 minutes
  - Should show progress for each engine
  - Look for "successfully trained" messages
- [ ] Training completes successfully:
  ```
  Training Direction Engine...
  Training Seller Engine...
  Training Buyer Engine...
  All models saved successfully!
  ```

### Phase 4: Verify Fix Worked
- [ ] Check if models load now:
  ```bash
  python -c "
  from seller.model import load_models
  t, r, b = load_models()
  print(f'Trap: {\"✅\" if t else \"❌\"}')
  print(f'Regime: {\"✅\" if r else \"❌\"}')
  print(f'Breach: {\"✅\" if b else \"❌\"}')
  "
  # Should show all ✅
  ```
- [ ] All three models show ✅ (loaded successfully)

### Phase 5: Test Inference
- [ ] Run single inference: `python infer.py`
  - Should complete without errors
  - Should generate/update `../aegismatrix.json`
- [ ] Check output JSON:
  ```bash
  cat ../aegismatrix.json | python -m json.tool | head -50
  # Look for trap and expiry_stress values
  ```
- [ ] Verify JSON contains calculated values (not errors)

### Phase 6: Commit Changes
- [ ] Go to root directory: `cd ..`
- [ ] Check git status: `git status`
  - Should show `models/` folder modified
- [ ] Stage changes:
  ```bash
  git add aegismatrix-engine/models/
  ```
- [ ] Verify staged changes: `git status`
  - Should show green/staged files
- [ ] Commit with message:
  ```bash
  git commit -m "🔧 Retrain models for numpy 2.x compatibility

  - seller_trap.pkl retrained
  - seller_regime.pkl retrained  
  - seller_breach.pkl retrained
  - buyer_breakout.pkl retrained
  - buyer_spike.pkl retrained
  - buyer_theta.pkl retrained
  - direction_seq.pt retrained

  Fixes volatility trap and expiry stress calculations that were
  falling back to heuristics due to numpy version mismatch.

  After this fix, metrics will update dynamically based on market conditions."
  ```
- [ ] Push to GitHub: `git push origin main`
  - May need to enter credentials
  - Should show "X files changed" message

### Phase 7: Verify Push
- [ ] Check GitHub online:
  - Go to your repository
  - Check "Commits" tab
  - Should see your recent commit
- [ ] Verify model files updated:
  - In repo, check `aegismatrix-engine/models/`
  - Timestamps should be recent

---

## 🎯 Post-Fix Verification

### Immediate Check (After commit)
- [ ] Models load successfully (Phase 4 check)
- [ ] Inference runs without errors (Phase 5 check)
- [ ] Changes committed to GitHub (Phase 6 check)

### Next Scheduled Run (30 minutes later)
- [ ] GitHub Actions workflow runs
- [ ] Check workflow logs:
  - No "numpy._core" errors
  - Models load successfully
- [ ] `aegismatrix.json` updates with new timestamp
- [ ] Volatility Trap shows new value (not 0.95)
- [ ] Expiry Stress shows new value (not 0.15)

### One Hour Later
- [ ] Check multiple runs (compare JSON timestamps)
- [ ] Values should vary between runs:
  - Trap: 0.87 → 0.92 → 0.84 (varies)
  - Stress: 0.42 → 0.38 → 0.45 (varies)
- [ ] Dashboard shows updated metrics

---

## ⚠️ Troubleshooting Checklist

### If Retraining Fails

**Error: `FileNotFoundError: data/nifty_daily.csv`**
- [ ] Download data first: `python data_fetcher.py`
- [ ] Retry: `python train_all.py`

**Error: `ModuleNotFoundError: No module named X`**
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Retry: `python train_all.py`

**Error: `CUDA out of memory`**
- [ ] Disable GPU: `CUDA_VISIBLE_DEVICES="" python train_all.py`
- [ ] Or use machine with more memory

**Error: `Permission denied`**
- [ ] Check folder permissions: `ls -la models/`
- [ ] Make writable: `chmod 755 models/`
- [ ] Retry: `python train_all.py`

### If Models Still Don't Load After Retrain

- [ ] Delete old models: `rm -f models/*.pkl models/*.pt`
- [ ] Retrain again: `python train_all.py`
- [ ] Verify files exist: `ls -lh models/`
  - Should show recent timestamps (current date)

### If Inference Still Fails

- [ ] Check error message carefully
- [ ] Verify features have data: Check `build_seller_features()` output
- [ ] Verify market data exists: Check `data/nifty_daily.csv`
- [ ] Try running with verbose logging:
  ```bash
  python -c "import logging; logging.basicConfig(level=logging.DEBUG); import infer"
  ```

---

## ✅ Success Criteria

### You Know It's Fixed When:

1. **Models Load** ✅
   - `python -c "from seller.model import load_models; t,r,b = load_models(); print(all([t,r,b]))"` returns `True`

2. **No Errors** ✅
   - `python infer.py` completes without errors
   - No `numpy._core` error messages
   - No ModelNotFoundError

3. **Values Update** ✅
   - Trap score differs from 0.95
   - Expiry stress differs from 0.15
   - Values vary between runs

4. **Changes Pushed** ✅
   - `git log` shows your recent commit
   - GitHub website shows updated models

5. **Next Run Works** ✅
   - GitHub Actions completes successfully
   - New `aegismatrix.json` generated
   - JSON timestamp is current

---

## 📊 Expected Results

### Before Fix
```
Volatility Trap: 0.95 (static)
Expiry Stress: 0.15 (static)
Historical Hit: 72% (static)
```

### After Fix
```
Volatility Trap: 0.87 → 0.92 → 0.84 (dynamic, ML predicted)
Expiry Stress: 0.42 → 0.38 → 0.45 (dynamic, ML predicted)
Historical Hit: 72% (still static - hard-coded, can fix later)
```

---

## ⏱️ Time Breakdown

| Phase | Task | Time |
|-------|------|------|
| 1 | Prepare & navigate | 2 min |
| 2 | Verify broken state | 1 min |
| 3 | Retrain models | 5 min |
| 4 | Verify fix | 1 min |
| 5 | Test inference | 2 min |
| 6 | Commit & push | 2 min |
| 7 | Verify push | 1 min |
| **Total** | | **~15 min** |

---

## 🎓 Next Steps (Optional)

After the main fix, you can optionally:

### Optional 1: Fix Hard-Coded Values
- [ ] Replace `historical_hit_rate = 0.72` with actual calculation
- [ ] Replace `historical_spike_rate = 0.58` with actual calculation
- [ ] Documents: See [CALCULATION_ANALYSIS.md](./CALCULATION_ANALYSIS.md)

### Optional 2: Verify All Metrics
- [ ] Check Direction predictions vary
- [ ] Check Buyer signals vary
- [ ] Check Safe Range varies
- [ ] Check Breach Probabilities vary

### Optional 3: Dashboard Verification
- [ ] Open dashboard in browser
- [ ] Verify tiles show new values
- [ ] Wait 30 minutes for next run
- [ ] Verify values changed again

---

## 🔗 Related Documents

- **[DIAGNOSIS_SUMMARY.md](./DIAGNOSIS_SUMMARY.md)** - Quick overview (read first!)
- **[COMPLETE_DIAGNOSIS.md](./COMPLETE_DIAGNOSIS.md)** - Full explanation
- **[NUMPY_COMPATIBILITY_FIX.md](./NUMPY_COMPATIBILITY_FIX.md)** - Detailed technical guide
- **[MODEL_LOADING_DEBUG.md](./MODEL_LOADING_DEBUG.md)** - Debugging info
- **[CALCULATION_ANALYSIS.md](./CALCULATION_ANALYSIS.md)** - Technical analysis

---

## 💾 Command Summary

```bash
# Navigate to engine
cd aegismatrix-engine

# Verify current status (optional)
python -c "from seller.model import load_models; t,r,b = load_models(); print('Loaded' if all([t,r,b]) else 'Failed')"

# THE FIX: Retrain models
python train_all.py

# Verify fix worked
python -c "from seller.model import load_models; t,r,b = load_models(); print('✅ Fixed!' if all([t,r,b]) else '❌ Still broken')"

# Test inference
python infer.py

# Go back and commit
cd ..
git add aegismatrix-engine/models/
git commit -m "🔧 Retrain models for numpy 2.x compatibility"
git push origin main
```

---

## ✨ Final Checklist

Before you say "I'm done":

- [ ] Read at least one diagnosis document
- [ ] Understood the root cause (numpy compatibility)
- [ ] Ran `python train_all.py` successfully
- [ ] Verified models load now
- [ ] Tested inference without errors
- [ ] Committed changes to GitHub
- [ ] Pushed to remote

**Once all checked: ✅ YOU'RE DONE! Dashboard will update on next run.** 🎉

---

## 📞 Questions?

If something goes wrong:

1. **Check troubleshooting section** above
2. **Read [NUMPY_COMPATIBILITY_FIX.md](./NUMPY_COMPATIBILITY_FIX.md)** for detailed error solutions
3. **Check GitHub Actions logs** for exact error messages
4. **Verify all documents** are in root directory

**Remember: The fix is simple, just retrain. You've got this!** 💪
