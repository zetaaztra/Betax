"""
Direction Engine Training Script - AegisCore

Trains two models:
1. BiLSTM Classifier: Predicts UP/DOWN/NEUTRAL (3-class)
2. XGBoost Regressor: Predicts expected move in points

Run locally on CPU (GPU optional). Output: .pt and .pkl model files
"""

import os
import sys
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import xgboost as xgb
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, mean_absolute_error, confusion_matrix
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import MODEL_DIR, DIRECTION_DEAD_ZONE, RANDOM_SEED
from data_fetcher import get_market_snapshots
from features.daily_features import build_direction_features

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ensure model directory exists
MODEL_DIR.mkdir(parents=True, exist_ok=True)


class BiLSTMClassifier(nn.Module):
    """
    Bidirectional LSTM for direction classification (UP/DOWN/NEUTRAL).
    
    Architecture:
    - Input: (batch, seq_len, features)
    - BiLSTM: hidden_size=128, num_layers=2, bidirectional
    - Attention: weighted pooling over time
    - Output: (batch, 3) logits for UP/DOWN/NEUTRAL
    """
    
    def __init__(self, input_size, hidden_size=128, num_layers=2, dropout=0.3):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0
        )
        
        # Attention mechanism
        self.attention = nn.Linear(hidden_size * 2, 1)
        
        # Classification head
        self.fc = nn.Sequential(
            nn.Linear(hidden_size * 2, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 3)  # 3 classes: DOWN, NEUTRAL, UP
        )
    
    def forward(self, x):
        """
        Args:
            x: (batch_size, seq_len, input_size)
        Returns:
            logits: (batch_size, 3)
        """
        # LSTM forward
        lstm_out, _ = self.lstm(x)  # (batch, seq_len, hidden_size*2)
        
        # Attention weights
        attn_scores = self.attention(lstm_out)  # (batch, seq_len, 1)
        attn_weights = torch.softmax(attn_scores.squeeze(-1), dim=1)  # (batch, seq_len)
        
        # Weighted pooling
        context = torch.sum(lstm_out * attn_weights.unsqueeze(-1), dim=1)  # (batch, hidden_size*2)
        
        # Classification
        logits = self.fc(context)
        return logits


def create_sequences(X, y, seq_len=60):
    """
    Create sequences for LSTM training.
    
    Args:
        X: (N, features)
        y: (N,)
        seq_len: sequence length
    
    Returns:
        X_seq: (N-seq_len, seq_len, features)
        y_seq: (N-seq_len,)
    """
    X_seq, y_seq = [], []
    for i in range(len(X) - seq_len):
        X_seq.append(X[i:i+seq_len])
        y_seq.append(y[i+seq_len])
    return np.array(X_seq), np.array(y_seq)


def create_labels(returns, dead_zone=DIRECTION_DEAD_ZONE):
    """
    Create 3-class labels from returns.
    
    Args:
        returns: daily returns array
        dead_zone: neutral zone (e.g., 0.2%)
    
    Returns:
        labels: 0=DOWN, 1=NEUTRAL, 2=UP
    """
    labels = np.zeros_like(returns, dtype=int)
    labels[returns > dead_zone] = 2  # UP
    labels[returns < -dead_zone] = 0  # DOWN
    labels[(returns >= -dead_zone) & (returns <= dead_zone)] = 1  # NEUTRAL
    return labels


def train_direction_classifier(X_seq, y_class, seq_len=60, epochs=50, batch_size=32):
    """Train BiLSTM classifier."""
    logger.info("=" * 60)
    logger.info("Training Direction Classifier (BiLSTM)")
    logger.info("=" * 60)
    
    # Train/val split
    train_size = int(0.8 * len(X_seq))
    X_train, X_val = X_seq[:train_size], X_seq[train_size:]
    y_train, y_val = y_class[:train_size], y_class[train_size:]
    
    # Normalize
    scaler = StandardScaler()
    X_train_flat = X_train.reshape(-1, X_train.shape[-1])
    X_val_flat = X_val.reshape(-1, X_val.shape[-1])
    
    X_train_flat = scaler.fit_transform(X_train_flat)
    X_val_flat = scaler.transform(X_val_flat)
    
    X_train = X_train_flat.reshape(X_train.shape)
    X_val = X_val_flat.reshape(X_val.shape)
    
    # Model
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Using device: {device}")
    
    model = BiLSTMClassifier(input_size=X_train.shape[-1]).to(device)
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.CrossEntropyLoss()
    
    # Training loop
    best_val_loss = float('inf')
    patience = 10
    patience_counter = 0
    
    for epoch in range(epochs):
        # Training
        model.train()
        train_loss = 0
        for i in range(0, len(X_train), batch_size):
            batch_X = torch.tensor(X_train[i:i+batch_size], dtype=torch.float32).to(device)
            batch_y = torch.tensor(y_train[i:i+batch_size], dtype=torch.long).to(device)
            
            optimizer.zero_grad()
            logits = model(batch_X)
            loss = loss_fn(logits, batch_y)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
        
        # Validation
        model.eval()
        with torch.no_grad():
            val_X = torch.tensor(X_val, dtype=torch.float32).to(device)
            val_y = torch.tensor(y_val, dtype=torch.long).to(device)
            val_logits = model(val_X)
            val_loss = loss_fn(val_logits, val_y).item()
            
            val_preds = torch.argmax(val_logits, dim=1).cpu().numpy()
            val_acc = accuracy_score(y_val, val_preds)
        
        if (epoch + 1) % 10 == 0:
            logger.info(f"Epoch {epoch+1}/{epochs} | Train Loss: {train_loss/len(X_train):.4f} | "
                       f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f}")
        
        # Early stopping
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            try:
                torch.save(model.state_dict(), str(MODEL_DIR / "direction_seq.pt"))
                logger.info(f"✓ Checkpoint saved at epoch {epoch+1}")
            except Exception as e:
                logger.warning(f"Failed to save checkpoint: {e}")
        else:
            patience_counter += 1
            if patience_counter >= patience:
                logger.info(f"Early stopping at epoch {epoch+1}")
                break
    
    logger.info(f"✓ Direction classifier trained. Best val accuracy: {val_acc:.4f}")
    
    # Final save with explicit error handling
    try:
        save_path = str(MODEL_DIR / "direction_seq.pt")
        torch.save(model.state_dict(), save_path)
        file_size = os.path.getsize(save_path)
        logger.info(f"✓ Model saved: {save_path} ({file_size} bytes)")
    except Exception as e:
        logger.error(f"Failed to save final model: {e}")
        logger.warning("Trying alternative save method...")
        try:
            torch.save(model, str(MODEL_DIR / "direction_seq.pt"))
            logger.info(f"✓ Full model saved as fallback")
        except Exception as e2:
            logger.error(f"Fallback save also failed: {e2}")
    
    # Confusion matrix
    cm = confusion_matrix(y_val, val_preds)
    logger.info(f"Confusion Matrix:\n{cm}")
    
    return scaler


def train_direction_magnitude(X_reg, y_points):
    """Train XGBoost regressor for expected move magnitude."""
    logger.info("=" * 60)
    logger.info("Training Direction Magnitude (XGBoost Regressor)")
    logger.info("=" * 60)
    
    # Train/val split
    X_train, X_val, y_train, y_val = train_test_split(
        X_reg, y_points, test_size=0.2, random_state=RANDOM_SEED
    )
    
    # Train XGBoost
    model = xgb.XGBRegressor(
        n_estimators=300,
        max_depth=7,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=RANDOM_SEED,
        n_jobs=-1
    )
    
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=False
    )
    
    # Validation
    y_pred = model.predict(X_val)
    mae = mean_absolute_error(y_val, y_pred)
    
    logger.info(f"✓ Direction magnitude trained. Val MAE: {mae:.2f} points")
    logger.info(f"✓ Model saved: {MODEL_DIR / 'direction_magnitude.pkl'}")
    
    joblib.dump(model, MODEL_DIR / "direction_magnitude.pkl")
    
    return model


def main():
    """Main training pipeline."""
    logger.info("Starting Direction Engine Training...")
    
    # Fetch data
    logger.info("Fetching market data...")
    nifty, vix = get_market_snapshots()
    
    if len(nifty) < 500:
        logger.error("Insufficient data for training")
        return
    
    logger.info(f"Loaded {len(nifty)} NIFTY rows, {len(vix)} VIX rows")
    
    # Build features
    logger.info("Building features...")
    features_df = build_direction_features(nifty, vix)
    
    if features_df is None or len(features_df) < 200:
        logger.error("Feature engineering failed")
        return
    
    logger.info(f"Built {len(features_df)} rows × {features_df.shape[1]} features")
    
    # Extract features and targets (only numeric columns)
    # Drop non-numeric columns (dates, timestamps, labels)
    numeric_cols = features_df.select_dtypes(include=[np.number]).columns
    X = features_df[numeric_cols].drop(columns=['target_return', 'target_points', 'label'], errors='ignore').values.astype(np.float32)
    
    # Create targets
    returns = nifty['Close'].pct_change().iloc[-len(features_df):].values
    y_class = create_labels(returns)
    y_points = np.abs(nifty['Close'].diff().iloc[-len(features_df):].values)
    
    # Create sequences for LSTM
    logger.info("Creating sequences...")
    X_seq, y_seq_class = create_sequences(X, y_class, seq_len=60)
    
    # Adjust y_points to match sequence length
    y_points_seq = y_points[60:]
    
    logger.info(f"Sequences: {X_seq.shape} | Classes: {y_seq_class.shape} | Points: {y_points_seq.shape}")
    
    # Train classifier
    scaler = train_direction_classifier(X_seq, y_seq_class)
    
    # Train magnitude
    train_direction_magnitude(X, y_points)
    
    logger.info("=" * 60)
    logger.info("✓ Direction training complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
