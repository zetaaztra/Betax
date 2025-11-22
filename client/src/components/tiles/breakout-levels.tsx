import { TileWrapper } from "./tile-wrapper";
import { BuyerData, MarketData } from "@shared/schema";
import { ArrowUp, ArrowDown } from "lucide-react";

interface BreakoutLevelsProps {
  buyer: BuyerData;
  market: MarketData;
  testId: string;
}

const helpText = "Breakout Reference Levels identify key price zones for option entry. Above upper level = breakout upside territory (buy calls). Below lower level = breakdown zone (buy puts). Between levels = no clear edge, wait. Use these as triggers rather than buying prematurely and bleeding theta.";

export function BreakoutLevels({ buyer, market, testId }: BreakoutLevelsProps) {
  const { upper, lower } = buyer.breakout_levels;
  const spot = market.spot;
  
  const upperDiff = upper - spot;
  const lowerDiff = spot - lower;

  return (
    <TileWrapper title="Breakout Reference Levels" helpText={helpText} testId={testId}>
      <div className="space-y-4">
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 bg-bullish/10 rounded-lg">
            <div className="flex items-center gap-2">
              <ArrowUp className="h-5 w-5 text-bullish" />
              <span className="text-sm font-medium">Breakout Up</span>
            </div>
            <span className="text-lg font-bold font-mono text-bullish">
              {upper.toFixed(0)}
            </span>
          </div>

          <div className="flex items-center justify-between p-3 bg-card border border-border rounded-lg">
            <span className="text-sm font-medium text-muted-foreground">Current Spot</span>
            <span className="text-lg font-bold font-mono">
              {spot.toFixed(0)}
            </span>
          </div>

          <div className="flex items-center justify-between p-3 bg-bearish/10 rounded-lg">
            <div className="flex items-center gap-2">
              <ArrowDown className="h-5 w-5 text-bearish" />
              <span className="text-sm font-medium">Breakdown</span>
            </div>
            <span className="text-lg font-bold font-mono text-bearish">
              {lower.toFixed(0)}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="text-center p-2 bg-bullish/10 rounded">
            <div className="text-muted-foreground">To Breakout</div>
            <div className="font-semibold font-mono text-bullish">
              +{upperDiff.toFixed(0)} pts
            </div>
          </div>
          <div className="text-center p-2 bg-bearish/10 rounded">
            <div className="text-muted-foreground">To Breakdown</div>
            <div className="font-semibold font-mono text-bearish">
              -{lowerDiff.toFixed(0)} pts
            </div>
          </div>
        </div>
      </div>
    </TileWrapper>
  );
}
