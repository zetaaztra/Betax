"""
Direction engine model predictions.
Handles horizon-based directional forecasts.
"""

import numpy as np
import logging
from pathlib import Path
import sys
import torch
import joblib

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import MODEL_DIR, DIRECTION_HORIZONS

logger = logging.getLogger(__name__)


def load_models():
    """
    Load pre-trained direction models.
    
    Returns:
        Tuple of (direction_model, magnitude_model, scaler)
    """
    try:
        # Load BiLSTM
        # We need to redefine the class or import it. 
        # Ideally it should be in a shared module, but for now we'll rely on the fact 
        # that torch.load might need the class definition if we saved the whole model,
        # but we saved state_dict. So we need to instantiate it.
        # However, we don't know input_size easily without the scaler or data.
        # BUT, we saved the scaler! The scaler's mean_ attribute has shape (n_features,).
        
        scaler_path = MODEL_DIR / "direction_scaler.pkl"
        if not scaler_path.exists():
            logger.warning("Scaler not found, returning None")
            return None, None, None
            
        scaler = joblib.load(scaler_path)
        input_size = scaler.mean_.shape[0]
        
        # Import class locally to avoid circular imports if any, 
        # or just define a helper to get the model structure.
        # For simplicity, we assume the class structure matches train_direction.py
        # We'll define a minimal version here or import if possible.
        # Since train_direction is a script, importing from it might run it.
        # So we will redefine the class here (or move it to a shared file in a refactor).
        # For this fix, I will redefine the class structure here to be safe.
        
        device = torch.device("cpu")
        direction_model = BiLSTMClassifier(input_size=input_size).to(device)
        
        model_path = MODEL_DIR / "direction_seq.pt"
        if model_path.exists():
            direction_model.load_state_dict(torch.load(model_path, map_location=device))
            direction_model.eval()
        else:
            logger.warning("Direction model not found")
            direction_model = None
            
        # Load Magnitude Model
        mag_path = MODEL_DIR / "direction_magnitude.pkl"
        if mag_path.exists():
            magnitude_model = joblib.load(mag_path)
        else:
            logger.warning("Magnitude model not found")
            magnitude_model = None
            
        return direction_model, magnitude_model, scaler
        
    except Exception as e:
        logger.error(f"Error loading direction models: {e}")
        return None, None, None


class BiLSTMClassifier(torch.nn.Module):
    """
    Bidirectional LSTM for direction classification (UP/DOWN/NEUTRAL).
    Must match training definition.
    """
    def __init__(self, input_size, hidden_size=128, num_layers=2, dropout=0.3):
        super().__init__()
        self.lstm = torch.nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0
        )
        self.attention = torch.nn.Linear(hidden_size * 2, 1)
        self.fc = torch.nn.Sequential(
            torch.nn.Linear(hidden_size * 2, 64),
            torch.nn.ReLU(),
            torch.nn.Dropout(dropout),
            torch.nn.Linear(64, 3)
        )
    
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        attn_scores = self.attention(lstm_out)
        attn_weights = torch.softmax(attn_scores.squeeze(-1), dim=1)
        context = torch.sum(lstm_out * attn_weights.unsqueeze(-1), dim=1)
        logits = self.fc(context)
        return logits


def predict_direction_horizons(features_df, models, horizons=DIRECTION_HORIZONS) -> dict:
    """
    Predict direction and magnitude for each horizon.
    
    Args:
        features_df: Feature DataFrame from daily_features
        models: Tuple (direction_model, magnitude_model, scaler)
        horizons: List of horizon days
        
    Returns:
        Dict keyed by horizon string (t1, t3, etc)
    """
    results = {}
    direction_model, magnitude_model, scaler = models
    
    # Handle empty dataframe or missing models
    if features_df is None or len(features_df) == 0 or direction_model is None:
        logger.warning("Empty features or missing models, generating placeholder predictions")
        for h in horizons:
            results[f"t{h}"] = {
                "direction": "NEUTRAL",
                "expected_move_points": 50.0,
                "conviction": 0.5
            }
        return results
    
    try:
        # Prepare data for BiLSTM
        # Need sequence of length 60
        seq_len = 60
        if len(features_df) < seq_len:
            logger.warning(f"Insufficient data for sequence (need {seq_len}, got {len(features_df)})")
            # Pad or just fail gracefully
            # Fallback to placeholder
            for h in horizons:
                results[f"t{h}"] = {
                    "direction": "NEUTRAL",
                    "expected_move_points": 50.0,
                    "conviction": 0.5
                }
            return results
            
        # Get last sequence
        numeric_cols = features_df.select_dtypes(include=[np.number]).columns
        # Ensure we drop non-feature columns if they exist
        X_raw = features_df[numeric_cols].drop(columns=['target_return', 'target_points', 'label'], errors='ignore').values.astype(np.float32)
        
        # Scale
        X_scaled = scaler.transform(X_raw)
        
        # Create sequence (1, 60, features)
        seq = X_scaled[-seq_len:].reshape(1, seq_len, -1)
        seq_tensor = torch.tensor(seq, dtype=torch.float32)
        
        # Predict Direction
        with torch.no_grad():
            logits = direction_model(seq_tensor)
            probs = torch.softmax(logits, dim=1).numpy()[0]
            pred_class = np.argmax(probs)
            
        # Map class to direction
        # 0=DOWN, 1=NEUTRAL, 2=UP
        class_map = {0: "DOWN", 1: "NEUTRAL", 2: "UP"}
        direction = class_map.get(pred_class, "NEUTRAL")
        conviction = float(probs[pred_class])
        
        # Predict Magnitude (XGBoost)
        # XGBoost takes the last row (current state)
        # But wait, the magnitude model was trained on the SAME features X.
        # XGBoost usually handles unscaled data fine, but we trained it on X_raw (unscaled) in train_direction.py?
        # Let's check train_direction.py: 
        # X = features_df[numeric_cols]...
        # train_direction_magnitude(X, y_points)
        # So it uses unscaled X.
        
        last_row = X_raw[-1].reshape(1, -1)
        
        if magnitude_model:
            expected_move_base = float(magnitude_model.predict(last_row)[0])
        else:
            expected_move_base = 50.0
            
        # Generate horizon-specific outputs
        # The models are trained for a general "next move" or specific horizon?
        # The training script creates labels based on 'returns' which is 1-day return?
        # train_direction.py: returns = nifty['Close'].pct_change()
        # So the classifier predicts T+1 direction.
        # The magnitude model predicts T+1 magnitude.
        
        # For longer horizons, we might need to project this or use separate models.
        # Since we only have one model trained on daily returns, we will extrapolate for now.
        # This is a limitation of the current training script, but we must work with it.
        
        for h in horizons:
            # Scale expected move by sqrt(time)
            # h is days. Model predicts 1 day.
            time_factor = np.sqrt(h)
            expected_move = expected_move_base * time_factor
            
            # Decay conviction for longer horizons
            horizon_conviction = max(0.1, conviction * (1 - np.log(h)/10)) # Simple decay
            
            results[f"t{h}"] = {
                "direction": direction,
                "expected_move_points": float(expected_move),
                "conviction": float(horizon_conviction)
            }
            
        logger.info(f"Generated predictions: {direction} ({conviction:.2f})")
        return results
        
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        # Fallback
        for h in horizons:
            results[f"t{h}"] = {
                "direction": "NEUTRAL",
                "expected_move_points": 50.0,
                "conviction": 0.5
            }
        return results


def predict_direction_risk_score(features_df) -> float:
    """
    Compute directional risk score (0-1).
    Higher = more uncertain.
    
    Args:
        features_df: Feature DataFrame
        
    Returns:
        Risk score 0-1
    """
    if features_df is None or len(features_df) == 0:
        logger.warning("Empty features_df, returning default risk score")
        return 0.5
    
    last_row = features_df.iloc[-1]
    
    # Simple heuristic
    vol = last_row.get("vol_20d", 0.01)
    normalized_vol = min(1.0, vol / 0.03)  # normalize to 0.03 as "high" vol
    
    risk_score = normalized_vol * 0.7 + np.random.randn() * 0.1
    risk_score = np.clip(risk_score, 0, 1)
    
    return float(risk_score)


def infer_regime(nifty_df, vix_df) -> str:
    """
    Infer current market regime.
    
    Args:
        nifty_df: NIFTY daily data
        vix_df: VIX daily data
        
    Returns:
        Regime label
    """
    last_nifty_row = nifty_df.iloc[-1]
    last_vix_row = vix_df.iloc[-1]
    
    recent_return = nifty_df["Close"].pct_change().tail(5).mean()
    vix_level = last_vix_row["Close"]
    
    if vix_level < 15 and recent_return > 0:
        regime = "LOW_VOL_BULL"
    elif vix_level > 25 and recent_return < 0:
        regime = "HIGH_VOL_BEAR"
    elif vix_level > 20 or abs(recent_return) < 0.001:
        regime = "SIDEWAYS_CHOP"
    else:
        regime = "TREND_FOLLOWING"
    
    return regime
