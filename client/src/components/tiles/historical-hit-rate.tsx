import { TileWrapper } from "./tile-wrapper";

interface HistoricalHitRateProps {
  rate: number;
  testId: string;
  context: "seller" | "buyer";
}

const sellerHelpText = "• Range Accuracy: How often NIFTY stayed in safe zones.\n• >75%: High reliability (Model is syncing well).\n• <60%: Caution (Market changing regime).\n• Use: Calibrate your position size based on this.";

const buyerHelpText = "• Spike Accuracy: Success rate of predicted breakouts.\n• >65%: Reliable signals (Aggressive entry).\n• <50%: Choppy market (Be selective).\n• Use: Validate breakout signals before entry.";

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
