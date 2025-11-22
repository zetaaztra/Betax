"""
Buyer Engine Training Script - PulseWave

Trains models for:
1. Breakout Probability Classifier (LightGBM - faster on CPU)
2. Spike Direction Classifier (predicts UP vs DOWN given a breakout)
3. Theta Edge Regressor

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
from sklearn.metrics import classification_report, roc_auc_score, mean_absolute_error
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import MODEL_DIR, RANDOM_SEED, BUYER_BREAKOUT_WINDOW
from data_fetcher import get_market_snapshots
from features.daily_features import build_buyer_features

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ensure model directory exists
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def create_breakout_labels(nifty_df, atr_multiplier=1.5, lookback=14):
    """
    Create binary breakout labels.
    
    Definition: Day has a spike if next day's range > current ATR * multiplier
    
    Args:
        nifty_df: OHLCV data
        atr_multiplier: threshold multiplier
        lookback: days for ATR calculation
    
    Returns:
        binary labels (breakout=1, no breakout=0)
    """
    labels = np.zeros(len(nifty_df) - 1, dtype=int)
    
    high_low = nifty_df['High'] - nifty_df['Low']
    high_close = np.abs(nifty_df['High'] - nifty_df['Close'].shift(1))
    low_close = np.abs(nifty_df['Low'] - nifty_df['Close'].shift(1))
    
    tr = np.maximum(high_low, np.maximum(high_close, low_close))
    atr = tr.rolling(window=lookback).mean()
    
    for i in range(lookback, len(nifty_df) - 1):
        current_atr = atr.iloc[i]
        next_range = nifty_df['High'].iloc[i+1] - nifty_df['Low'].iloc[i+1]
        
        if next_range > current_atr * atr_multiplier:
            labels[i] = 1  # Breakout
    
    return labels


def create_spike_direction_labels(nifty_df, lookback=14):
    """
    Create spike direction labels (UP=1, DOWN=0).
    
    Args:
        nifty_df: OHLCV data
        lookback: ATR calculation
    
    Returns:
        binary labels (where breakout occurred)
    """
    labels = np.zeros(len(nifty_df) - 1, dtype=int)
    
    high_low = nifty_df['High'] - nifty_df['Low']
    high_close = np.abs(nifty_df['High'] - nifty_df['Close'].shift(1))
    low_close = np.abs(nifty_df['Low'] - nifty_df['Close'].shift(1))
    
    tr = np.maximum(high_low, np.maximum(high_close, low_close))
    atr = tr.rolling(window=lookback).mean()
    
    for i in range(lookback, len(nifty_df) - 1):
        current_atr = atr.iloc[i]
        next_range = nifty_df['High'].iloc[i+1] - nifty_df['Low'].iloc[i+1]
        
        # Only label if there was a breakout
        if next_range > current_atr * 1.5:
            # UP if close > open
            labels[i] = 1 if nifty_df['Close'].iloc[i+1] > nifty_df['Open'].iloc[i+1] else 0
    
    return labels


def create_theta_edge_targets(nifty_df, lookback=14):
    """
    Create theta edge targets (continuous).
    
    Definition: Expected theta decay profit for a 1-day straddle
    Approximated by: daily range / 2 (simplified)
    
    Args:
        nifty_df: OHLCV data
        lookback: ATR window
    
    Returns:
        continuous values (0-1 range)
    """
    targets = np.zeros(len(nifty_df))
    
    daily_range = nifty_df['High'] - nifty_df['Low']
    atr = daily_range.rolling(window=lookback).mean()
    
    # Normalized theta edge: (actual range - expected range) / expected range
    # Where expected = prior day close * daily vol
    for i in range(1, len(nifty_df)):
        if atr.iloc[i] > 0:
            targets[i] = daily_range.iloc[i] / atr.iloc[i]
    
    # Normalize to 0-1
    targets = np.clip(targets / targets.max(), 0, 1) if targets.max() > 0 else targets
    
    return targets


def train_breakout_classifier(X, y_breakout):
    """Train XGBoost classifier for breakout prediction."""
    logger.info("=" * 60)
    logger.info("Training Breakout Classifier")
    logger.info("=" * 60)
    
    # Remove NaN
    valid_idx = ~(np.isnan(X).any(axis=1) | np.isnan(y_breakout))
    X = X[valid_idx]
    y_breakout = y_breakout[valid_idx]
    
    logger.info(f"Breakout label distribution: {np.bincount(y_breakout.astype(int))}")
    
    # Train/val split
    X_train, X_val, y_train, y_val = train_test_split(
        X, y_breakout, test_size=0.2, random_state=RANDOM_SEED
    )
    
    # Train model
    pos_weight = (y_train == 0).sum() / max((y_train == 1).sum(), 1)
    
    model = xgb.XGBClassifier(
        n_estimators=250,
        max_depth=7,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=RANDOM_SEED,
        scale_pos_weight=pos_weight,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_val)
    y_pred_proba = model.predict_proba(X_val)[:, 1]
    
    accuracy = (y_pred == y_val).mean()
    auc = roc_auc_score(y_val, y_pred_proba) if len(np.unique(y_val)) > 1 else 0.0
    
    logger.info(f"✓ Breakout classifier trained")
    logger.info(f"  Accuracy: {accuracy:.4f}")
    logger.info(f"  AUC-ROC: {auc:.4f}")
    logger.info(classification_report(y_val, y_pred, target_names=["No Breakout", "Breakout"]))
    
    joblib.dump(model, MODEL_DIR / "buyer_breakout.pkl")
    logger.info(f"✓ Model saved: {MODEL_DIR / 'buyer_breakout.pkl'}")
    
    return model


def train_spike_direction_classifier(X, y_spike_dir, y_breakout):
    """Train classifier for spike direction (UP vs DOWN given breakout)."""
    logger.info("=" * 60)
    logger.info("Training Spike Direction Classifier")
    logger.info("=" * 60)
    
    # Only use samples where breakout occurred
    breakout_idx = y_breakout == 1
    X_spike = X[breakout_idx]
    y_spike = y_spike_dir[breakout_idx]
    
    # Remove NaN
    valid_idx = ~(np.isnan(X_spike).any(axis=1) | np.isnan(y_spike))
    X_spike = X_spike[valid_idx]
    y_spike = y_spike[valid_idx]
    
    if len(X_spike) < 50:
        logger.warning(f"Insufficient breakout samples ({len(X_spike)}), skipping spike direction training")
        return None
    
    logger.info(f"Spike direction label distribution: {np.bincount(y_spike.astype(int))}")
    
    # Train/val split
    X_train, X_val, y_train, y_val = train_test_split(
        X_spike, y_spike, test_size=0.2, random_state=RANDOM_SEED
    )
    
    # Train model
    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.05,
        random_state=RANDOM_SEED,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_val)
    accuracy = (y_pred == y_val).mean()
    
    logger.info(f"✓ Spike direction classifier trained")
    logger.info(f"  Accuracy: {accuracy:.4f}")
    logger.info(classification_report(y_val, y_pred, target_names=["DOWN", "UP"]))
    
    joblib.dump(model, MODEL_DIR / "buyer_spike.pkl")
    logger.info(f"✓ Model saved: {MODEL_DIR / 'buyer_spike.pkl'}")
    
    return model


def train_theta_edge_regressor(X, y_theta):
    """Train regressor for theta edge score."""
    logger.info("=" * 60)
    logger.info("Training Theta Edge Regressor")
    logger.info("=" * 60)
    
    # Remove NaN
    valid_idx = ~(np.isnan(X).any(axis=1) | np.isnan(y_theta))
    X = X[valid_idx]
    y_theta = y_theta[valid_idx]
    
    # Train/val split
    X_train, X_val, y_train, y_val = train_test_split(
        X, y_theta, test_size=0.2, random_state=RANDOM_SEED
    )
    
    # Train model
    model = xgb.XGBRegressor(
        n_estimators=250,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=RANDOM_SEED,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_val)
    mae = mean_absolute_error(y_val, y_pred)
    
    logger.info(f"✓ Theta edge regressor trained")
    logger.info(f"  Val MAE: {mae:.4f}")
    
    joblib.dump(model, MODEL_DIR / "buyer_theta.pkl")
    logger.info(f"✓ Model saved: {MODEL_DIR / 'buyer_theta.pkl'}")
    
    return model


def main():
    """Main training pipeline."""
    logger.info("Starting Buyer Engine Training...")
    
    # Fetch data
    logger.info("Fetching market data...")
    nifty, vix = get_market_snapshots()
    
    if len(nifty) < 500:
        logger.error("Insufficient data for training")
        return
    
    logger.info(f"Loaded {len(nifty)} NIFTY rows, {len(vix)} VIX rows")
    
    # Build features
    logger.info("Building buyer features...")
    features_df = build_buyer_features(nifty, vix)
    
    if features_df is None or len(features_df) < 200:
        logger.error("Feature engineering failed")
        return
    
    logger.info(f"Built {len(features_df)} rows × {features_df.shape[1]} features")
    
    # Extract features (only numeric columns)
    numeric_cols = features_df.select_dtypes(include=[np.number]).columns
    X = features_df[numeric_cols].drop(columns=['label', 'target', 'return'], errors='ignore').values.astype(np.float32)
    
    # Create labels/targets
    logger.info("Creating labels and targets...")
    y_breakout = create_breakout_labels(nifty)
    y_spike_dir = create_spike_direction_labels(nifty)
    y_theta = create_theta_edge_targets(nifty)
    
    # Adjust arrays to same length
    min_len = min(len(X), len(y_breakout))
    X = X[:min_len]
    y_breakout = y_breakout[:min_len]
    y_spike_dir = y_spike_dir[:min_len]
    y_theta = y_theta[:min_len]
    
    logger.info(f"Label distribution - Breakout: {np.bincount(y_breakout.astype(int))}, "
               f"Theta range: [{y_theta.min():.4f}, {y_theta.max():.4f}]")
    
    # Train models
    train_breakout_classifier(X, y_breakout)
    train_spike_direction_classifier(X, y_spike_dir, y_breakout)
    train_theta_edge_regressor(X, y_theta)
    
    logger.info("=" * 60)
    logger.info("✓ Buyer training complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
