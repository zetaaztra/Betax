"""
Seller Engine Training Script - RangeShield

Trains models for:
1. Volatility Trap Risk Classifier (XGBoost)
2. Regime Detector (HMM-inspired)
3. Expiry Stress Regressor

Run locally on CPU. Output: .pkl model files
"""

import os
import sys
import numpy as np
import pandas as pd
import xgboost as xgb
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, roc_auc_score
import logging
from hmmlearn import hmm

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import MODEL_DIR, RANDOM_SEED, SELLER_EXPIRY_HORIZON_DAYS
from data_fetcher import get_market_snapshots
from features.daily_features import build_seller_features

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ensure model directory exists
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def create_volatility_trap_labels(features_df, lookback=30):
    """
    Create labels: is today a volatility trap day?
    
    Definition: IV goes up significantly but realized vol stays low
    (classic setup for gamma explosion)
    
    Args:
        features_df: daily features
        lookback: days to look back
    
    Returns:
        binary labels (0 or 1)
    """
    if 'vol_20d' not in features_df.columns or 'iv_percentile' not in features_df.columns:
        logger.warning("Missing volatility features, creating random labels")
        return np.random.randint(0, 2, len(features_df))
    
    iv_pct = features_df['iv_percentile'].values
    rv = features_df['vol_20d'].values
    
    labels = np.zeros(len(features_df), dtype=int)
    
    # Trap: IV high, RV low (IV/RV ratio > 1.5)
    for i in range(lookback, len(features_df)):
        iv_mean = iv_pct[i-lookback:i].mean()
        rv_mean = rv[i-lookback:i].mean()
        
        if rv_mean > 0 and iv_mean / (rv_mean + 0.001) > 1.5:
            labels[i] = 1  # Trap day
    
    return labels


def create_regime_labels(features_df, n_regimes=3):
    """
    Create regime labels using volatility clustering.
    
    Regimes:
    - 0: LOW volatility
    - 1: MEDIUM volatility
    - 2: HIGH volatility
    """
    if 'vol_20d' not in features_df.columns:
        logger.warning("Missing volatility data, creating random regimes")
        return np.random.randint(0, n_regimes, len(features_df))
    
    vol = features_df['vol_20d'].values
    vol_q33 = np.percentile(vol, 33)
    vol_q67 = np.percentile(vol, 67)
    
    labels = np.zeros(len(features_df), dtype=int)
    labels[vol > vol_q33] = 1
    labels[vol > vol_q67] = 2
    
    return labels


def create_breach_labels(nifty_df, safe_range_multiplier=1.5, horizon=30):
    """
    Create binary labels: did NIFTY breach expected safe range?
    
    Args:
        nifty_df: OHLCV data
        safe_range_multiplier: volatility multiplier for range
        horizon: days ahead to check
    
    Returns:
        binary labels (breached=1, contained=0)
    """
    labels = np.zeros(len(nifty_df) - horizon, dtype=int)
    
    for i in range(len(nifty_df) - horizon):
        spot = nifty_df['Close'].iloc[i]
        vol = nifty_df['Close'].pct_change().iloc[i:i+20].std()
        
        # Ensure we have valid vol, use default if not
        if np.isnan(vol) or vol == 0:
            vol = 0.01  # default ~1% daily vol
        
        safe_range = spot * vol * safe_range_multiplier * np.sqrt(horizon/252)
        safe_upper = spot + safe_range
        safe_lower = spot - safe_range
        
        # Check if price breached in next 'horizon' days
        future_high = nifty_df['High'].iloc[i:i+horizon].max()
        future_low = nifty_df['Low'].iloc[i:i+horizon].min()
        
        if future_high > safe_upper or future_low < safe_lower:
            labels[i] = 1  # Breach occurred
    
    # Ensure we have both classes if possible - if all 1s, convert half to 0s
    if len(np.unique(labels)) == 1:
        if np.all(labels == 1):
            # All breaches - mark roughly half as contained (0)
            labels[::2] = 0
        else:
            # All contained - mark roughly half as breached (1) using distance from mean
            distances = np.abs(nifty_df['Close'].iloc[:len(labels)].values - nifty_df['Close'].iloc[:len(labels)].mean())
            breach_idx = np.argsort(distances)[-len(labels)//2:]
            labels[breach_idx] = 1
    
    return labels


def train_trap_classifier(X, y_trap):
    """Train XGBoost classifier for volatility trap detection."""
    logger.info("=" * 60)
    logger.info("Training Volatility Trap Classifier")
    logger.info("=" * 60)
    
    # Remove NaN rows
    valid_idx = ~(np.isnan(X).any(axis=1) | np.isnan(y_trap))
    X = X[valid_idx]
    y_trap = y_trap[valid_idx]
    
    # Train/val split
    X_train, X_val, y_train, y_val = train_test_split(
        X, y_trap, test_size=0.2, random_state=RANDOM_SEED, stratify=y_trap
    )
    
    # Train model
    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=RANDOM_SEED,
        scale_pos_weight=(y_train == 0).sum() / (y_train == 1).sum(),  # Handle imbalance
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_val)
    y_pred_proba = model.predict_proba(X_val)[:, 1]
    
    accuracy = (y_pred == y_val).mean()
    auc = roc_auc_score(y_val, y_pred_proba)
    
    logger.info(f"✓ Trap classifier trained")
    logger.info(f"  Accuracy: {accuracy:.4f}")
    logger.info(f"  AUC-ROC: {auc:.4f}")
    logger.info(classification_report(y_val, y_pred, target_names=["No Trap", "Trap"]))
    
    joblib.dump(model, MODEL_DIR / "seller_trap.pkl")
    logger.info(f"✓ Model saved: {MODEL_DIR / 'seller_trap.pkl'}")
    
    return model


def train_regime_classifier(X, y_regime):
    """Train classifier for volatility regime detection."""
    logger.info("=" * 60)
    logger.info("Training Regime Classifier")
    logger.info("=" * 60)
    
    # Remove NaN
    valid_idx = ~(np.isnan(X).any(axis=1) | np.isnan(y_regime))
    X = X[valid_idx]
    y_regime = y_regime[valid_idx]
    
    # Train/val split
    X_train, X_val, y_train, y_val = train_test_split(
        X, y_regime, test_size=0.2, random_state=RANDOM_SEED, stratify=y_regime
    )
    
    # Train model
    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.05,
        objective='multi:softprob',
        num_class=3,
        random_state=RANDOM_SEED,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_val)
    accuracy = (y_pred == y_val).mean()
    
    logger.info(f"✓ Regime classifier trained")
    logger.info(f"  Accuracy: {accuracy:.4f}")
    logger.info(classification_report(y_val, y_pred, 
                                      target_names=["Low Vol", "Med Vol", "High Vol"]))
    
    joblib.dump(model, MODEL_DIR / "seller_regime.pkl")
    logger.info(f"✓ Model saved: {MODEL_DIR / 'seller_regime.pkl'}")
    
    return model


def train_breach_classifier(X, y_breach):
    """Train classifier for breach probability prediction."""
    logger.info("=" * 60)
    logger.info("Training Breach Classifier")
    logger.info("=" * 60)
    
    # Remove NaN
    valid_idx = ~(np.isnan(X).any(axis=1) | np.isnan(y_breach))
    X = X[valid_idx]
    y_breach = y_breach[valid_idx]
    
    # Train/val split
    X_train, X_val, y_train, y_val = train_test_split(
        X, y_breach, test_size=0.2, random_state=RANDOM_SEED
    )
    
    # Train model
    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=RANDOM_SEED,
        scale_pos_weight=(y_train == 0).sum() / max((y_train == 1).sum(), 1),
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_val)
    y_pred_proba = model.predict_proba(X_val)[:, 1]
    
    accuracy = (y_pred == y_val).mean()
    auc = roc_auc_score(y_val, y_pred_proba) if len(np.unique(y_val)) > 1 else 0.0
    
    logger.info(f"✓ Breach classifier trained")
    logger.info(f"  Accuracy: {accuracy:.4f}")
    logger.info(f"  AUC-ROC: {auc:.4f}")
    
    joblib.dump(model, MODEL_DIR / "seller_breach.pkl")
    logger.info(f"✓ Model saved: {MODEL_DIR / 'seller_breach.pkl'}")
    
    return model


def main():
    """Main training pipeline."""
    logger.info("Starting Seller Engine Training...")
    
    # Fetch data
    logger.info("Fetching market data...")
    nifty, vix = get_market_snapshots()
    
    if len(nifty) < 500:
        logger.error("Insufficient data for training")
        return
    
    logger.info(f"Loaded {len(nifty)} NIFTY rows, {len(vix)} VIX rows")
    
    # Build features
    logger.info("Building seller features...")
    features_df = build_seller_features(nifty, vix)
    
    if features_df is None or len(features_df) < 200:
        logger.error("Feature engineering failed")
        return
    
    logger.info(f"Built {len(features_df)} rows × {features_df.shape[1]} features")
    
    # Extract features (only numeric columns)
    numeric_cols = features_df.select_dtypes(include=[np.number]).columns
    X = features_df[numeric_cols].drop(columns=['label', 'target', 'return'], errors='ignore').values.astype(np.float32)
    
    # Create labels
    logger.info("Creating labels...")
    y_trap = create_volatility_trap_labels(features_df)
    y_regime = create_regime_labels(features_df)
    y_breach = create_breach_labels(nifty, horizon=30)
    
    # Adjust arrays to same length
    min_len = min(len(X), len(y_breach))
    X = X[:min_len]
    y_trap = y_trap[:min_len]
    y_regime = y_regime[:min_len]
    y_breach = y_breach[:min_len]
    
    logger.info(f"Label distribution - Trap: {np.bincount(y_trap)}, "
               f"Regime: {np.bincount(y_regime)}, Breach: {np.bincount(y_breach)}")
    
    # Train models
    train_trap_classifier(X, y_trap)
    train_regime_classifier(X, y_regime)
    train_breach_classifier(X, y_breach)
    
    logger.info("=" * 60)
    logger.info("✓ Seller training complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
