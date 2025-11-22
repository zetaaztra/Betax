import { AegisMatrixData } from "@shared/schema";
import { BreakoutGauge } from "@/components/tiles/breakout-gauge";
import { SpikeDirectionBias } from "@/components/tiles/spike-direction-bias";
import { ThetaEdgeScore } from "@/components/tiles/theta-edge-score";
import { BreakoutMap } from "@/components/tiles/breakout-map";
import { GammaWindows } from "@/components/tiles/gamma-windows";
import { BuyerRegime } from "@/components/tiles/buyer-regime";
import { HistoricalHitRate } from "@/components/tiles/historical-hit-rate";
import { BreakoutLevels } from "@/components/tiles/breakout-levels";
import { BuyerEnvironment } from "@/components/tiles/buyer-environment";
import { SpotPrice } from "@/components/tiles/spot-price";
import { VixIndicator } from "@/components/tiles/vix-indicator";
import { TileWrapper } from "@/components/tiles/tile-wrapper";
import { TileSkeleton } from "@/components/tiles/tile-skeleton";
import { Zap } from "lucide-react";

interface BuyerViewProps {
  data: AegisMatrixData | undefined;
}

export function BuyerView({ data }: BuyerViewProps) {
  if (!data) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
        {[...Array(12)].map((_, i) => (
          <TileSkeleton key={i} variant={i === 3 ? "bars" : i === 4 ? "grid" : i === 6 ? "chart" : "gauge"} />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
      {/* Row 1: Market Context */}
      <SpotPrice data={data.market} testId="tile-spot-price-buyer" />
      <VixIndicator data={data.market} testId="tile-vix-shock" emphasis="shock" />
      <BreakoutGauge data={data.buyer} testId="tile-breakout-gauge" />

      {/* Row 2: Buyer Signals */}
      <SpikeDirectionBias data={data.buyer} testId="tile-spike-direction" />
      <ThetaEdgeScore data={data.buyer} testId="tile-theta-edge" />
      <BreakoutMap data={data.buyer as any} testId="tile-breakout-map" />

      {/* Row 3: Analysis */}
      <GammaWindows data={data.buyer} testId="tile-gamma-windows" />
      <BuyerRegime data={data.buyer} testId="tile-buyer-regime" />
      <HistoricalHitRate rate={(data.buyer as any).historical_spike_rate} testId="tile-historical-spike-rate" context="buyer" />

      {/* Row 4: Final Metrics */}
      <BreakoutLevels buyer={data.buyer} market={data.market} testId="tile-breakout-levels" />
      <BuyerEnvironment data={data.buyer} testId="tile-buyer-environment" />
      <TileWrapper
        title="Help"
        helpText="This tab assesses whether buying options makes sense today. Breakout potential and theta-edge score are critical: don't buy if both are low. Spike direction bias helps choose calls vs puts. Gamma windows identify best intraday time blocks for entries. Buyer environment gives overall go/no-go guidance."
        testId="tile-help-buyer"
      >
        <div className="flex flex-col items-center justify-center h-full py-8">
          <Zap className="h-16 w-16 text-spike mb-4" />
          <p className="text-sm text-center text-muted-foreground px-4">
            PulseWave view for option buying edge
          </p>
        </div>
      </TileWrapper>
    </div>
  );
}
