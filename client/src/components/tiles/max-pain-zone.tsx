import { TileWrapper } from "./tile-wrapper";
import { SellerData } from "@shared/schema";

interface MaxPainZoneProps {
  data: SellerData;
  testId: string;
}

const helpText = "Max Pain Zone represents the strike price range where the maximum number of options (both calls and puts) expire worthless, causing maximum loss to option buyers. Market tends to gravitate toward this zone near expiry. Useful for predicting expiry-day pinning behavior and selecting short strikes.";

export function MaxPainZone({ data, testId }: MaxPainZoneProps) {
  const { lower, upper } = data.max_pain;
  const mid = (lower + upper) / 2;

  return (
    <TileWrapper title="Max Pain Zone" helpText={helpText} testId={testId}>
      <div className="space-y-4">
        <div className="flex flex-col items-center gap-2">
          <span className="text-xs text-muted-foreground">Max Pain Center</span>
          <span className="text-4xl font-bold font-mono text-primary">{mid.toFixed(0)}</span>
        </div>

        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Lower Bound</span>
            <span className="font-semibold font-mono">{lower.toFixed(0)}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Upper Bound</span>
            <span className="font-semibold font-mono">{upper.toFixed(0)}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Zone Width</span>
            <span className="font-semibold font-mono">{(upper - lower).toFixed(0)} pts</span>
          </div>
        </div>

        <div className="h-20 relative">
          <div className="absolute inset-0 flex items-end justify-center gap-1">
            {[...Array(15)].map((_, i) => {
              const height = 20 + Math.abs(7 - i) * 8;
              return (
                <div
                  key={i}
                  className={`flex-1 rounded-t ${i >= 5 && i <= 9 ? "bg-primary/40" : "bg-muted"}`}
                  style={{ height: `${100 - height}%` }}
                />
              );
            })}
          </div>
        </div>
      </div>
    </TileWrapper>
  );
}
