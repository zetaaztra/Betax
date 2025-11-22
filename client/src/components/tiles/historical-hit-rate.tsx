import { TileWrapper } from "./tile-wrapper";

interface HistoricalHitRateProps {
  rate: number;
  testId: string;
  context: "seller" | "buyer";
}

const sellerHelpText = "Historical Range Hit Rate shows how often NIFTY stayed within predicted safe ranges in the past. Higher rates (>75%) validate the model's accuracy. Lower rates (<60%) suggest increasing volatility or regime change. Use this to calibrate confidence in current safe range predictions.";

const buyerHelpText = "Historical Spike Hit Rate measures how often predicted breakout days actually delivered significant moves. High rate (>65%) indicates reliable signals. Low rate (<50%) means model struggling - be extra selective. This is your backtest validation for trusting current breakout forecasts.";

export function HistoricalHitRate({ rate, testId, context }: HistoricalHitRateProps) {
  const percentage = Math.round(rate * 100);
  
  const getLevel = () => {
    if (percentage >= 75) return { label: "High Accuracy", color: "text-bullish", bg: "bg-bullish/10" };
    if (percentage >= 60) return { label: "Moderate Accuracy", color: "text-neutral", bg: "bg-neutral/10" };
    return { label: "Low Accuracy", color: "text-bearish", bg: "bg-bearish/10" };
  };

  const level = getLevel();

  return (
    <TileWrapper 
      title={context === "seller" ? "Historical Range Hit Rate" : "Historical Spike Hit Rate"} 
      helpText={context === "seller" ? sellerHelpText : buyerHelpText} 
      testId={testId}
    >
      <div className="flex flex-col items-center gap-4">
        <div className="flex flex-col items-center gap-2">
          <span className="text-5xl font-bold font-mono">{percentage}%</span>
          <span className="text-xs text-muted-foreground">Historical Accuracy</span>
        </div>

        <div className={`px-4 py-2 rounded-lg ${level.bg} ${level.color} font-semibold`}>
          {level.label}
        </div>

        <div className="w-full space-y-1">
          <div className="h-3 bg-muted rounded-full overflow-hidden">
            <div 
              className={`h-full ${percentage >= 75 ? "bg-bullish" : percentage >= 60 ? "bg-neutral" : "bg-bearish"}`}
              style={{ width: `${percentage}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>0%</span>
            <span>50%</span>
            <span>100%</span>
          </div>
        </div>

        <div className="text-xs text-center text-muted-foreground">
          Based on last 30 trading days
        </div>
      </div>
    </TileWrapper>
  );
}
