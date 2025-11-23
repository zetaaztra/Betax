import { TileWrapper } from "./tile-wrapper";
import { BuyerData } from "@shared/schema";

interface GammaWindowsProps {
  data: BuyerData;
  testId: string;
}

const helpText = "Gamma Burst Windows identifies intraday time blocks when sharp price moves are most likely based on historical patterns and scheduled events. Bright colors = high-probability spike windows. Use this for day trading options: enter positions before hot windows, exit before cool periods to maximize gamma gains.";

export function GammaWindows({ data, testId }: GammaWindowsProps) {
  const windows = data.gamma_windows.map((w: any) => ({ ...w, score: w.score * 100 }));
  const maxScore = Math.max(...windows.map((w: any) => w.score));

  const getIntensityColor = (score: number) => {
    const intensity = score / maxScore;
    if (intensity > 0.7) return "bg-spike/60 text-spike-foreground";
    if (intensity > 0.4) return "bg-spike/30 text-foreground";
    return "bg-muted text-muted-foreground";
  };

  return (
    <TileWrapper title="Gamma Burst Windows (Intraday)" helpText={helpText} testId={testId}>
      <div className="space-y-3">
        <div className="grid grid-cols-6 gap-1">
          {windows.map((w: any, i: number) => (
            <div
              key={i}
              className={`p-2 rounded text-center ${getIntensityColor(w.score)}`}
            >
              <div className="text-xs font-semibold">{w.window}</div>
              <div className="text-xs font-mono mt-0.5">{w.score.toFixed(0)}</div>
            </div>
          ))}
        </div>

        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>09:15</span>
          <span>Market Hours</span>
          <span>15:30</span>
        </div>

        <div className="flex items-center gap-2 justify-center text-xs">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded bg-spike/60" />
            <span className="text-muted-foreground">High</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded bg-spike/30" />
            <span className="text-muted-foreground">Medium</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded bg-muted" />
            <span className="text-muted-foreground">Low</span>
          </div>
        </div>
      </div>
    </TileWrapper>
  );
}
