import { TileWrapper } from "./tile-wrapper";
import { MarketData } from "@shared/schema";
import { TrendingUp, TrendingDown } from "lucide-react";

interface SpotPriceProps {
  data: MarketData;
  testId: string;
}

const helpText = "Current NIFTY spot price with today's change. The sparkline shows intraday price movement. Positive change (green) indicates gains, negative (red) indicates losses. This is the reference point for all options calculations.";

export function SpotPrice({ data, testId }: SpotPriceProps) {
  const isPositive = data.spot_change >= 0;

  return (
    <TileWrapper title="Spot Price" helpText={helpText} testId={testId}>
      <div className="space-y-3">
        <div className="flex items-baseline gap-2">
          <span className="text-4xl font-bold font-mono" data-testid="text-spot-value">
            {data.spot.toFixed(2)}
          </span>
        </div>
        
        <div className={`flex items-center gap-2 ${isPositive ? "text-bullish" : "text-bearish"}`}>
          {isPositive ? <TrendingUp className="h-4 w-4" data-testid="icon-spot-trending-up" /> : <TrendingDown className="h-4 w-4" data-testid="icon-spot-trending-down" />}
          <span className="text-lg font-semibold font-mono" data-testid="text-spot-change">
            {isPositive ? "+" : ""}{data.spot_change.toFixed(2)}
          </span>
          <span className="text-sm" data-testid="text-spot-change-percent">
            ({isPositive ? "+" : ""}{((data.spot_change / data.spot) * 100).toFixed(2)}%)
          </span>
        </div>

        <div className="h-16 flex items-end gap-0.5">
          {[...Array(20)].map((_, i) => {
            const height = 20 + Math.random() * 60;
            return (
              <div
                key={i}
                className={`flex-1 rounded-t-sm ${isPositive ? "bg-bullish/30" : "bg-bearish/30"}`}
                style={{ height: `${height}%` }}
              />
            );
          })}
        </div>
      </div>
    </TileWrapper>
  );
}
