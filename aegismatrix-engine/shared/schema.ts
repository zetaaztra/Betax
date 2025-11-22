import { sql } from "drizzle-orm";
import { pgTable, text, varchar, real, integer, jsonb, timestamp } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

// Market Data Table
export const marketData = pgTable("market_data", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  spot: real("spot").notNull(),
  spotChange: real("spot_change").notNull(),
  vix: real("vix").notNull(),
  vixChange: real("vix_change").notNull(),
  regime: text("regime").notNull(),
  generatedAt: timestamp("generated_at").notNull().defaultNow(),
});

export const insertMarketDataSchema = createInsertSchema(marketData).omit({ id: true, generatedAt: true });
export type InsertMarketData = z.infer<typeof insertMarketDataSchema>;
export type MarketData = typeof marketData.$inferSelect;

// Direction Horizon Table
export const directionHorizon = pgTable("direction_horizon", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  marketDataId: varchar("market_data_id").notNull(),
  horizonType: text("horizon_type").notNull(), // "today", "t1", "t3", etc.
  direction: text("direction").notNull(),
  expectedMovePoints: real("expected_move_points").notNull(),
  conviction: real("conviction").notNull(),
  generatedAt: timestamp("generated_at").notNull().defaultNow(),
});

export const insertDirectionHorizonSchema = createInsertSchema(directionHorizon).omit({ id: true, generatedAt: true });
export type InsertDirectionHorizon = z.infer<typeof insertDirectionHorizonSchema>;
export type DirectionHorizon = typeof directionHorizon.$inferSelect;

// Direction Risk Table
export const directionRisk = pgTable("direction_risk", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  marketDataId: varchar("market_data_id").notNull(),
  riskScore: real("risk_score").notNull(),
  generatedAt: timestamp("generated_at").notNull().defaultNow(),
});

export const insertDirectionRiskSchema = createInsertSchema(directionRisk).omit({ id: true, generatedAt: true });
export type InsertDirectionRisk = z.infer<typeof insertDirectionRiskSchema>;
export type DirectionRisk = typeof directionRisk.$inferSelect;

// Seller Data Table
export const sellerData = pgTable("seller_data", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  marketDataId: varchar("market_data_id").notNull(),
  safeLower: real("safe_lower").notNull(),
  safeUpper: real("safe_upper").notNull(),
  maxPainLower: real("max_pain_lower").notNull(),
  maxPainUpper: real("max_pain_upper").notNull(),
  expiryStressScore: real("expiry_stress_score").notNull(),
  expiryStressLevel: text("expiry_stress_level").notNull(),
  trapScore: real("trap_score").notNull(),
  trapLevel: text("trap_level").notNull(),
  putSkew: real("put_skew").notNull(),
  callSkew: real("call_skew").notNull(),
  regime: text("regime").notNull(),
  historicalHitRate: real("historical_hit_rate").notNull(),
  dailyFlag: text("daily_flag").notNull(),
  breachProbabilities: jsonb("breach_probabilities").notNull(),
  generatedAt: timestamp("generated_at").notNull().defaultNow(),
});

export const insertSellerDataSchema = createInsertSchema(sellerData).omit({ id: true, generatedAt: true });
export type InsertSellerData = z.infer<typeof insertSellerDataSchema>;
export type SellerData = typeof sellerData.$inferSelect;

// Buyer Data Table
export const buyerData = pgTable("buyer_data", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  marketDataId: varchar("market_data_id").notNull(),
  breakoutTodayScore: real("breakout_today_score").notNull(),
  breakoutTodayLevel: text("breakout_today_level").notNull(),
  spikeUpProb: real("spike_up_prob").notNull(),
  spikeDownProb: real("spike_down_prob").notNull(),
  thetaEdgeScore: real("theta_edge_score").notNull(),
  thetaEdgeLevel: text("theta_edge_level").notNull(),
  regime: text("regime").notNull(),
  historicalSpikeRate: real("historical_spike_rate").notNull(),
  breakoutUpper: real("breakout_upper").notNull(),
  breakoutLower: real("breakout_lower").notNull(),
  environmentState: text("environment_state").notNull(),
  breakoutNext: jsonb("breakout_next").notNull(),
  gammaWindows: jsonb("gamma_windows").notNull(),
  generatedAt: timestamp("generated_at").notNull().defaultNow(),
});

export const insertBuyerDataSchema = createInsertSchema(buyerData).omit({ id: true, generatedAt: true });
export type InsertBuyerData = z.infer<typeof insertBuyerDataSchema>;
export type BuyerData = typeof buyerData.$inferSelect;

// Runtime validation schemas (for API responses - these validate the JSON structure)
export const marketDataSchema = z.object({
  spot: z.number(),
  spot_change: z.number(),
  vix: z.number(),
  vix_change: z.number(),
  regime: z.enum(["LOW_VOL_BULL", "HIGH_VOL_BULL", "LOW_VOL_BEAR", "HIGH_VOL_BEAR", "SIDEWAYS", "CHOPPY"]),
});

export const horizonDataSchema = z.object({
  direction: z.enum(["UP", "DOWN", "NEUTRAL"]),
  expected_move_points: z.number(),
  conviction: z.number().min(0).max(1),
});

export const directionDataSchema = z.object({
  today: horizonDataSchema,
  horizons: z.object({
    t1: horizonDataSchema,
    t3: horizonDataSchema,
    t5: horizonDataSchema,
    t10: horizonDataSchema,
    t20: horizonDataSchema,
    t40: horizonDataSchema,
  }),
  risk_score: z.number().min(0).max(1),
});

export const rangeSchema = z.object({
  lower: z.number(),
  upper: z.number(),
});

export const sellerDataResponseSchema = z.object({
  safe_range: rangeSchema,
  max_pain: rangeSchema,
  expiry_stress: z.object({
    score: z.number().min(0).max(100),
    level: z.enum(["LOW", "MEDIUM", "HIGH"]),
  }),
  trap: z.object({
    score: z.number().min(0).max(100),
    level: z.enum(["LOW", "MEDIUM", "HIGH"]),
  }),
  skew: z.object({
    put_skew: z.number(),
    call_skew: z.number(),
  }),
  regime: z.enum(["CALM", "CAUTIOUS", "HOSTILE"]),
  breach_probabilities: z.array(z.object({
    distance: z.number(),
    probability: z.number().min(0).max(1),
  })),
  historical_hit_rate: z.number().min(0).max(1),
  daily_flag: z.enum(["FAVOURABLE", "NEUTRAL", "RISKY"]),
});

export const buyerDataResponseSchema = z.object({
  breakout_today: z.object({
    score: z.number().min(0).max(100),
    level: z.enum(["LOW", "MODERATE", "HIGH"]),
  }),
  spike_direction_bias: z.object({
    up_prob: z.number().min(0).max(1),
    down_prob: z.number().min(0).max(1),
  }),
  theta_edge: z.object({
    score: z.number().min(0).max(100),
    level: z.enum(["POOR", "FAIR", "GOOD"]),
  }),
  breakout_next: z.array(z.object({
    day_offset: z.number(),
    score: z.number().min(0).max(100),
  })),
  gamma_windows: z.array(z.object({
    time_block: z.string(),
    score: z.number().min(0).max(100),
  })),
  regime: z.enum(["TREND_FOLLOWING", "MEAN_REVERTING", "CHOPPY"]),
  historical_spike_rate: z.number().min(0).max(1),
  breakout_levels: z.object({
    upper: z.number(),
    lower: z.number(),
  }),
  environment_state: z.enum(["PREMIUM_FRIENDLY", "CAUTIOUS", "AVOID_FULL_RISK"]),
});

export const aegisMatrixDataSchema = z.object({
  generated_at: z.string(),
  market: marketDataSchema,
  direction: directionDataSchema,
  seller: sellerDataResponseSchema,
  buyer: buyerDataResponseSchema,
});

// Type exports for runtime use
export type HorizonData = z.infer<typeof horizonDataSchema>;
export type DirectionData = z.infer<typeof directionDataSchema>;
export type SellerDataResponse = z.infer<typeof sellerDataResponseSchema>;
export type BuyerDataResponse = z.infer<typeof buyerDataResponseSchema>;
export type AegisMatrixData = z.infer<typeof aegisMatrixDataSchema>;
