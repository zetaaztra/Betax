import { TileWrapper } from "./tile-wrapper";
import { SellerData, MarketData } from "@shared/schema";

interface SafeRangeBandProps {
  seller: SellerData;
  market: MarketData;
  testId: string;
}

const helpText = "Safe Short Range shows price levels where selling options (strangles, iron condors) has historically favorable risk/reward. The band represents zones where NIFTY is likely to stay until expiry based on statistical analysis. Selling outside this range increases breach risk. Center marker shows current spot price.";

export function SafeRangeBand({ seller, market, testId }: SafeRangeBandProps) {
  const { lower, upper } = seller.safe_range;
  const spot = market.spot;
  const range = upper - lower;
  const spotPosition = ((spot - lower) / range) * 100;

  return (
    <TileWrapper title="Safe Short Range" helpText={helpText} testId={testId}>
      <div className="space-y-4">
        <div className="flex justify-between items-baseline">
          <div className="text-center">
            <div className="text-xs text-muted-foreground">Lower</div>
            <div className="text-lg font-bold font-mono text-bullish" data-testid={`text-safe-lower-${testId}`}>{lower.toFixed(0)}</div>
          </div>
          <div className="text-center">
            <div className="text-xs text-muted-foreground">Spot</div>
            <div className="text-2xl font-bold font-mono" data-testid={`text-safe-spot-${testId}`}>{spot.toFixed(0)}</div>
          </div>
          <div className="text-center">
            <div className="text-xs text-muted-foreground">Upper</div>
            <div className="text-lg font-bold font-mono text-bullish" data-testid={`text-safe-upper-${testId}`}>{upper.toFixed(0)}</div>
          </div>
        </div>

        <div className="relative">
          <div className="h-12 bg-muted rounded-lg relative overflow-hidden">
            <div className="absolute inset-y-0 left-0 right-0 bg-bullish/20" />
            <div 
              className="absolute top-1/2 -translate-y-1/2 w-1 h-full bg-foreground"
              style={{ left: `${spotPosition}%` }}
            />
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-xs font-semibold text-foreground/70">
                Safe Zone: {range.toFixed(0)} pts
              </span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="text-center p-2 bg-bullish/10 rounded">
            <div className="text-xs text-muted-foreground">Downside Buffer</div>
            <div className="font-semibold font-mono text-bullish" data-testid={`text-downside-buffer-${testId}`}>
              {(spot - lower).toFixed(0)} pts
            </div>
          </div>
          <div className="text-center p-2 bg-bullish/10 rounded">
            <div className="text-xs text-muted-foreground">Upside Buffer</div>
            <div className="font-semibold font-mono text-bullish" data-testid={`text-upside-buffer-${testId}`}>
              {(upper - spot).toFixed(0)} pts
            </div>
          </div>
        </div>
      </div>
    </TileWrapper>
  );
}
