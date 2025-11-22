import { TileWrapper } from "./tile-wrapper";
import { BuyerBlock } from "@/lib/aegis-data";

interface BreakoutMapProps {
  data: BuyerBlock;
  testId: string;
}

const helpText = "Next 5-Day Breakout Map forecasts which upcoming days have highest breakout probability. Taller bars = better days to hold options. Use this for timing: if tomorrow scores low but D+3 scores high, consider waiting to enter positions or choose longer expiry to capture the higher-probability day.";

export function BreakoutMap({ data, testId }: BreakoutMapProps) {
  const breakoutData = data.breakout_next;

  // Convert 0-1 scores to 0-100 for display
  const scores = breakoutData.map(d => d.score * 100);
  // Use a lower floor for max score (e.g. 40) so that low scores still show visible bars
  const maxScore = Math.max(...scores, 40);
  const minScore = Math.min(...scores, 0);
  const range = maxScore - minScore || 1;

  return (
    <TileWrapper title="Next 5-Day Breakout Map" helpText={helpText} testId={testId}>
      <div className="space-y-4">
        <div className="h-32 flex items-end justify-between gap-2">
          {breakoutData.map((d, i) => {
            const scoreDisplay = scores[i];
            // Normalize to 0-100% for bar height
            const height = ((scoreDisplay - minScore) / range) * 100;
            const isHigh = scoreDisplay > 65;
            return (
              <div key={i} className="flex-1 flex flex-col items-center gap-1">
                <div className="flex-1 flex flex-col justify-end w-full">
                  <div
                    className={`w-full rounded-t transition-all duration-300 ${isHigh ? "bg-spike/60" : "bg-neutral/50"
                      }`}
                    style={{ height: `${Math.max(height, 10)}%` }}
                  />
                </div>
                <div className="text-xs text-muted-foreground">
                  D+{d.day_offset}
                </div>
              </div>
            );
          })}
        </div>

        <div className="grid grid-cols-5 gap-1 text-xs">
          {scores.map((score, i) => (
            <div key={i} className="text-center">
              <div className={`font-semibold font-mono ${score > 65 ? "text-spike" : "text-foreground"}`}>
                {Math.round(score)}
              </div>
            </div>
          ))}
        </div>

        <div className="text-center text-xs text-muted-foreground">
          Score represents breakout probability (0-100)
        </div>
      </div>
    </TileWrapper>
  );
}
