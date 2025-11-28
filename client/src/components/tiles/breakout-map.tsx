import { TileWrapper } from "./tile-wrapper";
import { BuyerBlock } from "@/lib/aegis-data";

interface BreakoutMapProps {
  data: BuyerBlock;
  testId: string;
}

const helpText = "• Numbers show breakout chance out of 100.\n• Below 5: Very low (choppy market, avoid buying options).\n• 5-20: Low-Moderate (selective buying only).\n• 20-50: Moderate (decent setup for buyers).\n• Above 50: High (strong breakout potential).\n• Strategy: Only buy options on days with score >20.";

export function BreakoutMap({ data, testId }: BreakoutMapProps) {
  const breakoutData = data.breakout_next;

  // Convert 0-1 scores to 0-100 for display
  // Heuristic: If scores are small (<= 5), assume they are probabilities and scale to 0-100
  // Force conversion to number to avoid string/NaN issues
  let scores = breakoutData.map(d => Number(d.score) || 0);
  const rawMax = Math.max(...scores);

  // If the max value is small (e.g. 0.6 or 1.0), it's likely a probability 0-1.
  // We want to display it as 0-100.
  if (rawMax <= 5.0 && rawMax > 0) {
    scores = scores.map(s => s * 100);
  }

  // Dynamic scaling: find the max score in the dataset to scale bars relatively
  // We use a minimum denominator of 1 to avoid division by zero
  const maxScore = Math.max(...scores);
  const minScore = 0;
  const range = maxScore - minScore || 1;

  return (
    <TileWrapper title="Next 5-Day Breakout Map" helpText={helpText} testId={testId}>
      <div className="space-y-4">
        {/* Removed items-end to allow columns to stretch to full height */}
        <div className="h-32 flex justify-between gap-2">
          {breakoutData.map((d, i) => {
            const scoreDisplay = scores[i];
            // Normalize to 0-100% for bar height
            const height = ((scoreDisplay - minScore) / range) * 100;
            const isHigh = scoreDisplay > 65;
            return (
              <div key={i} className="flex-1 flex flex-col items-center gap-1">
                <div className="flex-1 flex flex-col justify-end w-full">
                  <div
                    className={`w-full rounded-t transition-all duration-300 ${isHigh ? "bg-spike" : "bg-sky-500/60"
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
                {score.toFixed(1)}
              </div>
            </div>
          ))}
        </div>

        <div className="text-center text-xs text-muted-foreground">
          Breakout probability (0-100 scale)
        </div>
      </div>
    </TileWrapper>
  );
}
