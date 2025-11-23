"""
Central configuration for AegisMatrix engine.
No business logic - only constants and paths.
"""

from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent
CLIENT_ROOT = PROJECT_ROOT / "client"
JSON_OUTPUT_PATH = CLIENT_ROOT / "public" / "data" / "aegismatrix.json"
MODEL_DIR = PROJECT_ROOT / "models"
DATA_DIR = PROJECT_ROOT / "data"

# Market symbols
NIFTY_SYMBOL = "^NSEI"
VIX_SYMBOL = "^INDIAVIX"

# Data parameters
LOOKBACK_YEARS = 5
INTRADAY_PERIOD = "5d"
INTRADAY_INTERVAL = "5m"

# Direction engine
DIRECTION_HORIZONS = [1, 3, 5, 10, 20, 40]  # t+1, t+3, t+5, t+10, t+20, t+40 days

# Seller engine
SELLER_EXPIRY_HORIZON_DAYS = 30
SAFE_RANGE_MULTIPLIER = 1.5  # volatility multiplier for safety band

# Buyer engine
BUYER_BREAKOUT_WINDOW = 14  # days for ORB

# Feature parameters
FEATURE_LOOKBACK = 60  # days for rolling features
VOL_WINDOW_SHORT = 10
VOL_WINDOW_MED = 20
VOL_WINDOW_LONG = 60
ATR_PERIOD = 14

# Training parameters (for local training only)
SEQUENCE_LENGTH = 60  # days for LSTM sequence
VALIDATION_SPLIT = 0.2
RANDOM_SEED = 42

# Thresholds
DIRECTION_DEAD_ZONE = 0.002  # 0.2% dead zone for UP/DOWN/NEUTRAL labels
