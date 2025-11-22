"""
JSON schema validation for aegismatrix.json using Pydantic.
Ensures frontend never breaks due to missing or malformed fields.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal
from datetime import datetime


# Direction Block Models
class DirectionHorizon(BaseModel):
    label: str = Field(..., description="Human-readable horizon (e.g., 'Tomorrow')")
    direction: Literal["UP", "DOWN", "NEUTRAL"]
    expected_move_points: float = Field(..., description="Expected move in points (signed)")
    conviction: float = Field(..., ge=0, le=1, description="Confidence 0-1")


class DirectionToday(BaseModel):
    direction: Literal["UP", "DOWN", "NEUTRAL"]
    expected_move_points: float
    conviction: float = Field(..., ge=0, le=1)
    intraday_volatility_score: float = Field(..., ge=0, le=1)
    last_update: str = Field(..., description="ISO8601 with timezone")


class DirectionBlock(BaseModel):
    today: DirectionToday
    horizons: Dict[str, DirectionHorizon]
    risk_score: float = Field(..., ge=0, le=1)


# Market Block
class MarketBlock(BaseModel):
    spot: float
    spot_change: float
    spot_change_pct: float
    vix: float
    vix_change: float
    vix_change_pct: float
    regime: Literal["LOW_VOL_BULL", "HIGH_VOL_BEAR", "SIDEWAYS_CHOP", "TREND_FOLLOWING"]


# Seller Block Models
class SafeRange(BaseModel):
    lower: float
    upper: float
    horizon_days: int


class MaxPain(BaseModel):
    lower: float
    upper: float
    confidence: float = Field(..., ge=0, le=1)


class TrapRisk(BaseModel):
    score: float = Field(..., ge=0, le=1)
    label: Literal["LOW", "MEDIUM", "HIGH"]
    iv_percentile: float = Field(..., ge=0, le=1)
    rv_percentile: float = Field(..., ge=0, le=1)


class Skew(BaseModel):
    put_skew: float = Field(..., ge=-1, le=1)
    call_skew: float = Field(..., ge=-1, le=1)
    net_skew: float = Field(..., ge=-1, le=1)


class ExpiryStress(BaseModel):
    score: float = Field(..., ge=0, le=1)
    label: Literal["CALM", "CAUTION", "HOSTILE"]


class BreachProbability(BaseModel):
    distance: int = Field(..., gt=0, description="Points away from spot")
    probability: float = Field(..., ge=0, le=1)


class SellerFlag(BaseModel):
    label: Literal["FAVOURABLE", "CAUTION", "HOSTILE"]
    color: Literal["GREEN", "AMBER", "RED"]
    reasons: List[str]


class SellerBlock(BaseModel):
    safe_range: SafeRange
    max_pain: MaxPain
    trap: TrapRisk
    skew: Skew
    expiry_stress: ExpiryStress
    breach_probabilities: List[BreachProbability]
    seller_flag: SellerFlag


# Buyer Block Models
class BuyerScore(BaseModel):
    score: float = Field(..., ge=0, le=1)
    label: Literal["LOW", "MEDIUM", "HIGH"]


class BreakoutNext(BaseModel):
    day_offset: int = Field(..., ge=1, le=5)
    score: float = Field(..., ge=0, le=1)
    label: Literal["LOW", "MEDIUM", "HIGH"]


class SpikeDirectionBias(BaseModel):
    up_prob: float = Field(..., ge=0, le=1)
    down_prob: float = Field(..., ge=0, le=1)


class GammaWindow(BaseModel):
    window: str = Field(..., description="HH:MM-HH:MM format")
    score: float = Field(..., ge=0, le=1)


class ThetaEdge(BaseModel):
    score: float = Field(..., ge=0, le=1)
    label: Literal["DONT_WASTE_PREMIUM", "BORDERLINE", "EDGE_JUSTIFIES_PREMIUM"]


class BuyerEnvironment(BaseModel):
    label: Literal["PREMIUM_FRIENDLY", "SPECULATIVE_ONLY", "UNFAVOURABLE"]
    color: Literal["GREEN", "AMBER", "RED"]
    reasons: List[str]


class BuyerBlock(BaseModel):
    breakout_today: BuyerScore
    breakout_next: List[BreakoutNext]
    spike_direction_bias: SpikeDirectionBias
    gamma_windows: List[GammaWindow]
    theta_edge: ThetaEdge
    regime: Literal["TREND_FOLLOWING", "MEAN_REVERT", "CHOPPY"]
    buyer_environment: BuyerEnvironment


# Top-level schema
class AegisMatrixPayload(BaseModel):
    generated_at: str = Field(..., description="ISO8601 UTC string")
    market: MarketBlock
    direction: DirectionBlock
    seller: SellerBlock
    buyer: BuyerBlock


def validate_payload(payload: dict) -> None:
    """
    Validate payload against schema. Raises ValidationError if invalid.
    
    Args:
        payload: Dict to validate
        
    Raises:
        pydantic.ValidationError
    """
    AegisMatrixPayload(**payload)
