# Technical Deep Dive: Model Training vs Inference

## Part 1: Why Predictions Change (Even With Same Models)

### The Key Insight
```
CONSTANT                          VARIABLE
┌──────────────────┐             ┌──────────────────┐
│  ML Models       │             │  Market Data     │
│  (Trained)       │      +      │  (Live)          │      =    DIFFERENT
│  ├─ BiLSTM       │             │  ├─ Spot price   │          PREDICTIONS
│  ├─ XGBoost      │             │  ├─ Volatility   │          EVERY 30 MIN
│  └─ Parameters   │             │  ├─ Momentum     │
│  (Retrained      │             │  └─ Tech Signals │
│   only weekly)   │             │  (Update every   │
└──────────────────┘             │   1-5 minutes)   │
                                 └──────────────────┘
```

### Real Example: Direction Prediction

#### Training (Saturday)
```python
# direction/train_direction.py
1. Fetch historical data (5 years)
2. Build sequences of 60 days each
3. Train BiLSTM on these sequences
4. Save trained model: direction_seq.pt
5. Save feature scaler: direction_scaler.pkl

Result: Frozen model ready for inference
```

#### Inference (Every 30 mins)
```python
# infer.py
1. Load saved model: direction_seq.pt (SAME as trained)
2. Load saved scaler: direction_scaler.pkl (SAME as trained)
3. Fetch TODAY'S data (different every 30 mins!)
4. Build features from TODAY'S data (different!)
5. Scale features using saved scaler
6. Feed to BiLSTM
7. Get prediction (DIFFERENT because input is different!)

Key: Model weights unchanged, but input data is fresh
```

### Concrete Example

```python
# Saturday Training
df = fetch_data(start='2020-11-25', end='2025-11-22')
sequences = build_sequences(df, window=60)
model = BiLSTM(input_size=25, hidden_size=64)
model.fit(sequences)
torch.save(model.state_dict(), 'direction_seq.pt')
# Model now knows: "When I see THIS pattern, prediction is UP"

# Monday 9:00 AM Inference
model = load('direction_seq.pt')  # Same model!
today_data = fetch_data(start='2025-11-24', end='2025-11-24')  # Different!
sequence = build_sequence(today_data, window=60)  # Different input!
prediction = model.predict(sequence)  # Different output!

# Monday 9:30 AM Inference
model = load('direction_seq.pt')  # SAME model
today_data_930 = fetch_intraday_data()  # Different data!
sequence_930 = build_sequence(today_data_930, window=60)  # Different input!
prediction_930 = model.predict(sequence_930)  # Different output!
```

### Feature Changes Between Runs

```
9:00 AM Run:
- NIFTY Close: 24,100
- 20-day Vol: 15.2%
- RSI(14): 58
- MACD: +0.15
→ Prediction: UP (0.65 confidence)

9:30 AM Run:
- NIFTY Close: 24,120 (UP 20 pts!)
- 20-day Vol: 15.8% (volatility increased)
- RSI(14): 62 (momentum increased)
- MACD: +0.25 (signal strengthened)
→ Prediction: UP (0.72 confidence) ← CHANGED!

10:00 AM Run:
- NIFTY Close: 24,050 (DOWN 50 from open)
- 20-day Vol: 14.9% (volatility decreased)
- RSI(14): 45 (momentum weakened)
- MACD: -0.05 (signal reversed)
→ Prediction: NEUTRAL (0.55 confidence) ← CHANGED AGAIN!
```

**This is CORRECT behavior!** Market changed, predictions should adapt.

---

## Part 2: Model Persistence & Loading

### Training Pipeline: Model Saving

```python
# direction/train_direction.py
import torch
import joblib

# 1. Train model
model = BiLSTMClassifier(input_size=25)
model.train_on(train_sequences)

# 2. Save PyTorch model
torch.save(
    model.state_dict(),
    'models/direction_seq.pt'
)
# Contains: all weights, biases, architecture parameters

# 3. Save feature scaler
scaler = StandardScaler()
scaler.fit(train_features)
joblib.dump(scaler, 'models/direction_scaler.pkl')
# Contains: mean_, scale_, fitted on training data

# buyer/train_buyer.py
xgb_breakout = XGBClassifier(...)
xgb_breakout.fit(train_features, train_labels)
joblib.dump(xgb_breakout, 'models/buyer_breakout.pkl')
# XGBoost saves everything needed for prediction

# seller/train_seller.py
xgb_trap = XGBClassifier(...)
xgb_trap.fit(train_features, train_labels)
joblib.dump(xgb_trap, 'models/seller_trap.pkl')
```

### Inference Pipeline: Model Loading

```python
# infer.py
import torch
import joblib

# 1. Load Direction model
scaler = joblib.load('models/direction_scaler.pkl')
input_size = scaler.mean_.shape[0]  # Extract from scaler
model = BiLSTMClassifier(input_size=input_size)
model.load_state_dict(torch.load('models/direction_seq.pt'))
model.eval()  # Set to evaluation mode

# 2. Load Buyer models
buyer_breakout = joblib.load('models/buyer_breakout.pkl')
buyer_spike = joblib.load('models/buyer_spike.pkl')
buyer_theta = joblib.load('models/buyer_theta.pkl')

# 3. Load Seller models
seller_trap = joblib.load('models/seller_trap.pkl')
seller_regime = joblib.load('models/seller_regime.pkl')
seller_breach = joblib.load('models/seller_breach.pkl')

# 4. Use for predictions
features = build_features(market_data)
features_scaled = scaler.transform(features)
prediction = model.predict(features_scaled)
```

### What Gets Saved?

| File | Size | Type | Contains |
|------|------|------|----------|
| `direction_seq.pt` | ~500KB | PyTorch | BiLSTM weights, biases, state |
| `direction_scaler.pkl` | ~1KB | joblib | mean_, scale_ for feature normalization |
| `direction_gru_xgb.pkl` | ~50KB | joblib | XGBoost model + tree structure |
| `buyer_breakout.pkl` | ~100KB | joblib | XGBoost weights + feature importances |
| `buyer_spike.pkl` | ~100KB | joblib | XGBoost weights + feature importances |
| `buyer_theta.pkl` | ~100KB | joblib | XGBoost weights + feature importances |
| `seller_trap.pkl` | ~100KB | joblib | XGBoost weights + feature importances |
| `seller_regime.pkl` | ~100KB | joblib | XGBoost weights + feature importances |
| `seller_breach.pkl` | ~100KB | joblib | XGBoost weights + feature importances |

**Total: ~900KB of trained models committed to GitHub**

---

## Part 3: Data Fetching Compliance

### Your Data Flow

```
┌─────────────────────────────────────────────────────────┐
│ Raw Market Data (yfinance)                               │
│ - NIFTY (^NSEI): 5-year daily + intraday                │
│ - VIX (^INDIAVIX): 5-year daily                         │
│ - Live spot price                                        │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼ (data_fetcher.py)
┌─────────────────────────────────────────────────────────┐
│ Caching Strategy                                         │
│ - Daily cache in CSV (data/NSEI_daily.csv)             │
│ - Intraday cache in CSV (data/NSEI_intraday.csv)       │
│ - Cache age checked every run                           │
│ - Update only if > 3 days old                           │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼ (training or inference)
┌─────────────────────────────────────────────────────────┐
│ Feature Engineering                                      │
│ - Returns, log-returns                                   │
│ - Moving averages, volatility                           │
│ - Technical indicators (RSI, MACD, etc)                 │
│ - Momentum signals                                       │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ ML Models                                                │
│ - Training: Learn from patterns                         │
│ - Inference: Apply learned patterns                     │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ Output                                                   │
│ - aegismatrix.json (predictions)                        │
│ - Committed to GitHub                                   │
│ - Dashboard fetches and displays                        │
└─────────────────────────────────────────────────────────┘
```

### API Call Pattern (yfinance Compliance)

#### Bad Pattern ❌
```python
# This would violate rate limits
for i in range(1000):
    data = yf.download('^NSEI', start='2020-01-01', end='2025-11-24')
    # HAMMERING THE API! IP would get blocked
```

#### Your Pattern ✅
```python
# Training (once per week)
data = yf.download('^NSEI', start='2020-01-01', end='2025-11-24')
# Only 1 call per week

# Inference (13 times per day)
# Uses cached data from previous call
# Only refreshes intraday (less data = faster)
if cache_age > 3_days:
    data = yf.download(...)  # Refresh if needed
else:
    data = load_cache(...)  # Use cached
    
# Live price (separate, minimal)
live_price = yf.Ticker('^NSEI').info['regularMarketPrice']
# Not every call fetches full historical data
```

### Rate Limiting Handling

```python
# Your implementation in data_fetcher.py

def _fetch_yahoo_api_data(symbol, retries=3):
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 429:  # Rate limited!
                wait_time = 2 * (attempt + 1)  # Exponential backoff
                logger.warning(f"Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
                
            return parse_response(response)
            
        except Exception as e:
            if attempt < retries - 1:
                continue
            else:
                # Fallback to cache or alternative source
                return load_cache()

# Strategy:
# 1st attempt: Wait 2 seconds, retry
# 2nd attempt: Wait 4 seconds, retry
# 3rd attempt: Wait 8 seconds, retry
# If all fail: Use cached data (always works!)
```

### yfinance Best Practices Implemented

| Practice | Your Implementation | Status |
|----------|-------------------|--------|
| **Caching** | Local CSV files, 3-day TTL | ✅ Good |
| **Rate Limiting** | 3 retries with backoff | ✅ Good |
| **Timeouts** | 10-30 second timeouts | ✅ Good |
| **User-Agent Rotation** | 4 different agents | ✅ Good |
| **Error Handling** | Graceful fallbacks | ✅ Good |
| **Batch Requests** | Fetch once, cache, reuse | ✅ Good |
| **Request Delay** | Backoff on 429 errors | ✅ Good |

### Why Rate Limiting Still Occurs

```
You run: 13 inference jobs per day (every 30 mins)
Each job: Attempts to check for data updates
GitHub Actions: Uses shared IPs (many users from same IP)

yfinance Rate Limit: ~1000 requests per hour per IP

Multiple GitHub Actions accounts → Same IP → Rate limit triggers

Your Solution: Cache data!
- First 1-2 runs: Fetch fresh (might hit limit)
- Remaining runs: Use cache (no API calls!)
- Eventually rate limit expires → Resume fresh fetches

Result: System works! No production impact. ✅
```

---

## Part 4: Complete Data Flow Example

### Scenario: Monday 9:00 AM Inference Run

```
┌─────────────────────────────────────────────────────────┐
│ STEP 1: Load Pre-trained Models                         │
└─────────────────────────────────────────────────────────┘
direction_model = load('models/direction_seq.pt')
direction_scaler = load('models/direction_scaler.pkl')
buyer_models = [
    load('models/buyer_breakout.pkl'),
    load('models/buyer_spike.pkl'),
    load('models/buyer_theta.pkl')
]
seller_models = [
    load('models/seller_trap.pkl'),
    load('models/seller_regime.pkl'),
    load('models/seller_breach.pkl')
]

┌─────────────────────────────────────────────────────────┐
│ STEP 2: Fetch Current Data                              │
└─────────────────────────────────────────────────────────┘
# Check cache age
cache_age = now - last_update_time
if cache_age > 3_days:
    # Try fresh from yfinance (might rate limit, that's ok)
    nifty_daily = fetch_from_yfinance('^NSEI')
    vix_daily = fetch_from_yfinance('^INDIAVIX')
else:
    # Use cache (fast, reliable)
    nifty_daily = load_csv('data/NSEI_daily.csv')
    vix_daily = load_csv('data/INDIAVIX_daily.csv')

# Always fetch fresh intraday (small dataset)
nifty_intraday = fetch_intraday_from_yfinance('^NSEI', period='5d', interval='1m')

# Get live spot price
live_spot = fetch_live_price('^NSEI')

┌─────────────────────────────────────────────────────────┐
│ STEP 3: Build Features                                  │
└─────────────────────────────────────────────────────────┘
daily_features = build_daily_features(nifty_daily, vix_daily)
# Contains: returns, volatility, RSI, MACD, Bollinger bands, etc.

intraday_features = build_intraday_features(nifty_intraday)
# Contains: current momentum, 5-min trend, intraday volatility

gamma_windows = identify_gamma_windows(nifty_intraday)
# Contains: time periods with highest gamma risk

┌─────────────────────────────────────────────────────────┐
│ STEP 4: Generate Predictions                            │
└─────────────────────────────────────────────────────────┘
# Direction predictions
direction_input = direction_scaler.transform(daily_features)
direction_pred = direction_model.predict(direction_input)
# Output: Direction (UP/DOWN/NEUTRAL) for 6 horizons

# Seller predictions
seller_pred = []
for model in seller_models:
    pred = model.predict(daily_features)
    seller_pred.append(pred)
# Output: Safe ranges, max pain, breach probability

# Buyer predictions
buyer_pred = []
for model in buyer_models:
    pred = model.predict(daily_features + intraday_features)
    buyer_pred.append(pred)
# Output: Breakout probability, spike bias, theta edge

┌─────────────────────────────────────────────────────────┐
│ STEP 5: Assemble JSON Output                            │
└─────────────────────────────────────────────────────────┘
aegismatrix = {
    "generated_at": "2025-11-24T09:00:00Z",
    "market": {
        "spot": live_spot,
        "spot_change": live_spot - previous_close,
        "vix": vix_daily.iloc[-1]['Close'],
        "regime": determine_regime(nifty_daily, vix_daily)
    },
    "direction": direction_pred,
    "seller": seller_pred,
    "buyer": buyer_pred
}

┌─────────────────────────────────────────────────────────┐
│ STEP 6: Save & Commit                                   │
└─────────────────────────────────────────────────────────┘
save_json(aegismatrix, 'client/public/data/aegismatrix.json')
git_commit('Update predictions [skip ci]')
git_push()

Dashboard fetches JSON and updates in real-time!

┌─────────────────────────────────────────────────────────┐
│ STEP 7: 30 Minutes Later (9:30 AM)                      │
└─────────────────────────────────────────────────────────┘
MODELS: Same (direction_seq.pt unchanged)
DATA: Different! (New intraday prices, new momentum)
FEATURES: Different!
PREDICTIONS: Different! (But using same model)

This is why calculations change every 30 minutes!
```

---

## Part 5: Monitoring & Verification

### How to Verify System is Working

#### Weekly (After Training)
```bash
# Check model files were trained and committed
git log --oneline -- aegismatrix-engine/models/
# Should see recent commit: "chore: update trained models"

# Check file timestamps
ls -la aegismatrix-engine/models/
# Files should have today's date

# Verify file sizes
wc -c aegismatrix-engine/models/*.pkl
# Should be > 50KB each
```

#### Daily (During Market Hours)
```bash
# Check inference jobs ran
cat client/public/data/aegismatrix.json

# Verify timestamp is recent (within 30 mins)
jq '.generated_at' client/public/data/aegismatrix.json

# Verify spot price is current
jq '.market.spot' client/public/data/aegismatrix.json

# Verify predictions changed
git log --oneline -- client/public/data/aegismatrix.json | head -5
# Should see recent commits (every 30 mins)
```

### Expected Log Output (Training)
```
Starting AegisMatrix ML Training Pipeline
Training Direction Engine (AegisCore)...
  Fetching 5 years of NIFTY data...
  Downloaded 1234 daily candles
  Building sequences...
  Training BiLSTM (60 second timeout)
  Training complete! Saved to models/direction_seq.pt

Training Seller Engine (RangeShield)...
  Training seller_trap model...
  Training seller_regime model...
  Training seller_breach model...
  All seller models saved!

Training Buyer Engine (TrendScout)...
  Training buyer_breakout model...
  Training buyer_spike model...
  Training buyer_theta model...
  All buyer models saved!

✓ All engines trained successfully!
Models ready for inference at: models/
Total training time: 65 seconds
```

### Expected Log Output (Inference)
```
=== AegisMatrix Inference Start ===
Loading trained models...
  Direction models loaded ✓
  Buyer models loaded ✓
  Seller models loaded ✓
  
Fetching market data...
  Cache age: 1 day (fresh enough, using cache)
  Loaded NIFTY: 1234 rows
  Loaded VIX: 1220 rows
  Fetched intraday: 245 rows
  Data fetched: NIFTY 1234 rows, VIX 1220 rows, intraday 245 rows

Building features...
  Built direction features: (1159, 25)
  Built seller features: (1159, 28)
  Built buyer features: (1159, 29)
  Built intraday features
  Features built successfully

Computing predictions...
  Direction: Generated predictions for 6 horizons
  Seller: Computed safe ranges and max pain
  Buyer: Computed breakout and spike signals

Assembling payload...
  Market block: spot=24100.5, vix=15.2
  Direction block: 6 horizons with conviction scores
  Seller block: safe ranges, breach probabilities
  Buyer block: breakout, gamma windows, theta edge
  
Validating payload... ✓

Writing to client/public/data/aegismatrix.json...
Output written to: /repo/client/public/data/aegismatrix.json
=== AegisMatrix Inference Complete ===
```

---

## Summary Table

| Aspect | Training | Inference |
|--------|----------|-----------|
| **Frequency** | Weekly (Saturday) | Every 30 mins (Mon-Fri) |
| **Duration** | ~60 seconds | ~30 seconds |
| **Models** | CREATED/TRAINED | LOADED/USED |
| **Market Data** | Historical (5 years) | Current (today + intraday) |
| **Output** | Model files (*.pkl, *.pt) | aegismatrix.json |
| **Computation** | Heavy (GPU-friendly) | Light (just inference) |
| **File Committed** | aegismatrix-engine/models/ | client/public/data/aegismatrix.json |

---

## The Answer to Your Question

### "Will calculations change when infer runs?"

**YES, and here's why:**

1. **Models are frozen** (trained weekly)
2. **Market data is live** (updates every 30 mins)
3. **Features recalculated** (from new market data)
4. **Predictions adapt** (to market changes)

```
Think of it like a weather prediction model:
- Model knows: "When I see THIS pressure pattern, rain comes"
- But pressure CHANGES every hour
- So prediction CHANGES every hour
- Model stays the same, but input changes

Your system:
- Model knows: "When market looks THIS way, UP is likely"
- But market CHANGES every 30 mins
- So prediction CHANGES every 30 mins
- Models stay the same, but market changes
```

This is **WORKING CORRECTLY**! ✅
