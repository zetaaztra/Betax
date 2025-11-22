import { TileWrapper } from "./tile-wrapper";
import { MarketData } from "@shared/schema";
import { Activity } from "lucide-react";

interface VixIndicatorProps {
  data: MarketData;
  testId: string;
  emphasis?: "shock" | "normal";
}

const helpText = "India VIX (Volatility Index) measures market fear and uncertainty. Low VIX (<15) suggests calm markets favorable for option sellers. Medium VIX (15-25) indicates normal volatility. High VIX (>25) signals turbulent conditions requiring caution.";

const shockHelpText = "VIX Shock Risk indicates potential for sudden market gaps and volatility spikes. High VIX increases option premiums but also risk of adverse moves. Option buyers may find opportunities during VIX spikes, while sellers should reduce position sizes.";

export function VixIndicator({ data, testId, emphasis = "normal" }: VixIndicatorProps) {
  const getVixLevel = () => {
    if (data.vix < 15) return { label: "Low", color: "text-bullish", bg: "bg-bullish/10" };
    if (data.vix < 25) return { label: "Normal", color: "text-neutral", bg: "bg-neutral/10" };
    return { label: "High", color: "text-bearish", bg: "bg-bearish/10" };
  };

  const level = getVixLevel();
  const isPositive = data.vix_change >= 0;

  return (
    <TileWrapper 
      title={emphasis === "shock" ? "VIX Shock Risk" : "India VIX"} 
      helpText={emphasis === "shock" ? shockHelpText : helpText} 
      testId={testId}
    >
      <div className="space-y-4">
        <div className="flex items-baseline gap-3">
          <span className="text-4xl font-bold font-mono" data-testid={`text-vix-value-${testId}`}>
            {data.vix.toFixed(1)}
          </span>
          <span className={`text-lg font-semibold font-mono ${isPositive ? "text-bearish" : "text-bullish"}`} data-testid={`text-vix-change-${testId}`}>
            {isPositive ? "+" : ""}{data.vix_change.toFixed(1)}
          </span>
        </div>

        <div className={`flex items-center gap-2 p-3 rounded-lg ${level.bg}`}>
          <Activity className={`h-5 w-5 ${level.color}`} />
          <span className={`font-semibold ${level.color}`} data-testid={`text-vix-level-${testId}`}>{level.label} Volatility</span>
        </div>

        <div className="space-y-1">
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>Low</span>
            <span>Normal</span>
            <span>High</span>
          </div>
          <div className="h-2 bg-muted rounded-full overflow-hidden flex">
            <div className="flex-1 bg-bullish/50" />
            <div className="flex-1 bg-neutral/50" />
            <div className="flex-1 bg-bearish/50" />
          </div>
          <div className="relative h-1">
            <div 
              className="absolute w-0.5 h-4 bg-foreground rounded-full -top-1.5"
              style={{ left: `${Math.min((data.vix / 40) * 100, 100)}%` }}
            />
          </div>
        </div>
      </div>
    </TileWrapper>
  );
}
