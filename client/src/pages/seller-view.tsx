import { AegisMatrixData } from "@shared/schema";
import { SafeRangeBand } from "@/components/tiles/safe-range-band";
import { MaxPainZone } from "@/components/tiles/max-pain-zone";
import { ExpiryStressMeter } from "@/components/tiles/expiry-stress-meter";
import { VolatilityTrap } from "@/components/tiles/volatility-trap";
import { SkewPressure } from "@/components/tiles/skew-pressure";
import { SellerRegime } from "@/components/tiles/seller-regime";
import { BreachCurve } from "@/components/tiles/breach-curve";
import { HistoricalHitRate } from "@/components/tiles/historical-hit-rate";
import { SellerDailyFlag } from "@/components/tiles/seller-daily-flag";
import { SpotPrice } from "@/components/tiles/spot-price";
import { VixIndicator } from "@/components/tiles/vix-indicator";
import { TileWrapper } from "@/components/tiles/tile-wrapper";
import { TileSkeleton } from "@/components/tiles/tile-skeleton";
import { Shield } from "lucide-react";

interface SellerViewProps {
  data: AegisMatrixData | undefined;
}

export function SellerView({ data }: SellerViewProps) {
  if (!data) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
        {[...Array(12)].map((_, i) => (
          <TileSkeleton key={i} variant={i === 0 ? "grid" : i === 4 ? "bars" : i === 6 ? "chart" : "gauge"} />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
      {/* Row 1: Market Context */}
      <SpotPrice data={data.market} testId="tile-spot-price" />
      <VixIndicator data={data.market} testId="tile-vix" />
      <SafeRangeBand seller={data.seller} market={data.market} testId="tile-safe-range" />

      {/* Row 2: More Seller Metrics */}
      <MaxPainZone data={data.seller} testId="tile-max-pain" />
      <ExpiryStressMeter data={data.seller} testId="tile-expiry-stress" />
      <VolatilityTrap data={data.seller} testId="tile-volatility-trap" />

      {/* Row 3: Risk Metrics */}
      <SkewPressure data={data.seller} testId="tile-skew-pressure" />
      <SellerRegime data={data.seller} testId="tile-seller-regime" />
      <BreachCurve data={data.seller as any} testId="tile-breach-curve" />

      {/* Row 4: Final Metrics */}
      <HistoricalHitRate rate={(data.seller as any).historical_hit_rate} testId="tile-historical-hit-rate-seller" context="seller" />
      <SellerDailyFlag data={data.seller} testId="tile-seller-daily-flag" />
      <TileWrapper
        title="Help"
        helpText="This tab helps option sellers identify safe zones and risk levels. The safe range shows where to place short strikes. Expiry stress and volatility trap warn of potential dangers. Use seller regime and daily flag for go/no-go decisions on aggressive short selling. Remember: selling options is high risk - always use stop losses."
        testId="tile-help-seller"
      >
        <div className="flex flex-col items-center justify-center h-full py-8">
          <Shield className="h-16 w-16 text-bullish mb-4" />
          <p className="text-sm text-center text-muted-foreground px-4">
            RangeShield view for safe option selling
          </p>
        </div>
      </TileWrapper>
    </div>
  );
}
