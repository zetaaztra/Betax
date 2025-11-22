/**
 * AegisMatrix data loader and type definitions
 * Loads aegismatrix.json and provides typed access to all engines
 */

export interface AegisMatrixData {
  generated_at: string;
  market: MarketBlock;
  direction: DirectionBlock;
  seller: SellerBlock;
  buyer: BuyerBlock;
}

// Market Block
export interface MarketBlock {
  spot: number;
  spot_change: number;
  spot_change_pct: number;
  vix: number;
  vix_change: number;
  vix_change_pct: number;
  regime: "LOW_VOL_BULL" | "HIGH_VOL_BEAR" | "SIDEWAYS_CHOP" | "TREND_FOLLOWING";
}

// Direction Block
export interface DirectionToday {
  direction: "UP" | "DOWN" | "NEUTRAL";
  expected_move_points: number;
  conviction: number;
  intraday_volatility_score: number;
  last_update: string;
}

export interface DirectionHorizon {
  label: string;
  direction: "UP" | "DOWN" | "NEUTRAL";
  expected_move_points: number;
  conviction: number;
}

export interface DirectionBlock {
  today: DirectionToday;
  horizons: Record<string, DirectionHorizon>;
  risk_score: number;
}

// Seller Block
export interface SafeRange {
  lower: number;
  upper: number;
  horizon_days: number;
}

export interface MaxPain {
  lower: number;
  upper: number;
  confidence: number;
}

export interface TrapRisk {
  score: number;
  label: "LOW" | "MEDIUM" | "HIGH";
  iv_percentile: number;
  rv_percentile: number;
}

export interface Skew {
  put_skew: number;
  call_skew: number;
  net_skew: number;
}

export interface ExpiryStress {
  score: number;
  label: "CALM" | "CAUTION" | "HOSTILE";
}

export interface BreachProbability {
  distance: number;
  probability: number;
}

export interface SellerFlag {
  label: "FAVOURABLE" | "CAUTION" | "HOSTILE";
  color: "GREEN" | "AMBER" | "RED";
  reasons: string[];
}

export interface SellerBlock {
  safe_range: SafeRange;
  max_pain: MaxPain;
  trap: TrapRisk;
  skew: Skew;
  expiry_stress: ExpiryStress;
  breach_probabilities: BreachProbability[];
  seller_flag: SellerFlag;
}

// Buyer Block
export interface BuyerScore {
  score: number;
  label: "LOW" | "MEDIUM" | "HIGH";
}

export interface BreakoutNext {
  day_offset: number;
  score: number;
  label: "LOW" | "MEDIUM" | "HIGH";
}

export interface SpikeDirectionBias {
  up_prob: number;
  down_prob: number;
}

export interface GammaWindow {
  window: string;
  score: number;
}

export interface ThetaEdge {
  score: number;
  label: "DONT_WASTE_PREMIUM" | "BORDERLINE" | "EDGE_JUSTIFIES_PREMIUM";
}

export interface BuyerEnvironment {
  label: "PREMIUM_FRIENDLY" | "SPECULATIVE_ONLY" | "UNFAVOURABLE";
  color: "GREEN" | "AMBER" | "RED";
  reasons: string[];
}

export interface BuyerBlock {
  breakout_today: BuyerScore;
  breakout_next: BreakoutNext[];
  spike_direction_bias: SpikeDirectionBias;
  gamma_windows: GammaWindow[];
  theta_edge: ThetaEdge;
  regime: "TREND_FOLLOWING" | "MEAN_REVERT" | "CHOPPY";
  buyer_environment: BuyerEnvironment;
}

// Data loader
let cachedData: AegisMatrixData | null = null;
let cacheTimestamp: number = 0;
const CACHE_TTL = 60000; // 1 minute cache

/**
 * Load AegisMatrix data from public JSON file
 * Uses in-memory cache to avoid repeated fetches
 */
export async function loadAegisMatrixData(
  forceRefresh = false
): Promise<AegisMatrixData> {
  const now = Date.now();

  if (cachedData && !forceRefresh && now - cacheTimestamp < CACHE_TTL) {
    return cachedData;
  }

  try {
    const response = await fetch("/data/aegismatrix.json", {
      headers: {
        "Cache-Control": "no-cache",
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to load aegismatrix.json: ${response.status}`);
    }

    cachedData = (await response.json()) as AegisMatrixData;
    cacheTimestamp = now;
    return cachedData;
  } catch (error) {
    console.error("Error loading AegisMatrix data:", error);
    throw error;
  }
}

/**
 * Clear the cache
 */
export function clearAegisMatrixCache() {
  cachedData = null;
  cacheTimestamp = 0;
}

/**
 * Get last generated timestamp
 */
export function getLastGeneratedTime(): string | null {
  return cachedData?.generated_at ?? null;
}
