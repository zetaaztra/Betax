import { AegisMatrixData } from "@shared/schema";
import { DirectionGauge } from "@/components/tiles/direction-gauge";
import { SpotPrice } from "@/components/tiles/spot-price";
import { VixIndicator } from "@/components/tiles/vix-indicator";
import { RiskScoreDial } from "@/components/tiles/risk-score-dial";
import { MarketRegime } from "@/components/tiles/market-regime";
import { TileWrapper } from "@/components/tiles/tile-wrapper";
import { TileSkeleton } from "@/components/tiles/tile-skeleton";
import { HelpCircle } from "lucide-react";

interface DirectionViewProps {
  data: AegisMatrixData | undefined;
}

export function DirectionView({ data }: DirectionViewProps) {
  if (!data) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
        {[...Array(12)].map((_, i) => (
          <TileSkeleton key={i} variant={i === 0 ? "gauge" : i === 1 ? "numeric" : i === 6 || i === 7 ? "chart" : "gauge"} />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
      {/* Row 1: Market Context */}
      <SpotPrice data={data.market} testId="tile-spot-price" />
      <VixIndicator data={data.market} testId="tile-vix" />
      <DirectionGauge data={data.direction.today} title="Today Direction" testId="tile-today-direction" />
      
      {/* Row 2: More Predictions */}
      <DirectionGauge data={data.direction.horizons.t1} title="Tomorrow (T+1)" testId="tile-t1" />
      <DirectionGauge data={data.direction.horizons.t3} title="Next 3 Days (T+3)" testId="tile-t3" />
      <DirectionGauge data={data.direction.horizons.t5} title="This Week (T+5)" testId="tile-t5" />
      
      {/* Row 3: More Horizons */}
      <DirectionGauge data={data.direction.horizons.t10} title="Next Week (T+10)" testId="tile-t10" />
      <DirectionGauge data={data.direction.horizons.t20} title="This Month (T+20)" testId="tile-t20" />
      <DirectionGauge data={data.direction.horizons.t40} title="Next Month (T+40)" testId="tile-t40" />
      
      {/* Row 4: Risk & Regime */}
      <RiskScoreDial score={data.direction.risk_score} testId="tile-risk-score" />
      <MarketRegime data={data.market} testId="tile-market-regime" />
      <TileWrapper 
        title="Help" 
        helpText="This tab shows NIFTY's expected directional movement across multiple time horizons. Use shorter horizons (today, T+1, T+3) for day trading and swing trades. Use longer horizons (T+10, T+20, T+40) for position planning and monthly options. The risk score and market regime provide overall context for risk management." 
        testId="tile-help-direction"
      >
        <div className="flex flex-col items-center justify-center h-full py-8">
          <HelpCircle className="h-16 w-16 text-primary mb-4" />
          <p className="text-sm text-center text-muted-foreground px-4">
            Click the <span className="text-foreground font-semibold">?</span> icon on any tile for detailed explanations
          </p>
        </div>
      </TileWrapper>
    </div>
  );
}
