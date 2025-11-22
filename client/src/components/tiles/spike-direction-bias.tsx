import { TileWrapper } from "./tile-wrapper";
import { BuyerData } from "@shared/schema";
import { ArrowUp, ArrowDown } from "lucide-react";

interface SpikeDirectionBiasProps {
  data: BuyerData;
  testId: string;
}

const helpText = "Spike Direction Bias shows if a breakout occurs, which direction is more probable. Use this to choose between calls or puts when buying options. Strong bias (>70%) suggests clear directional conviction. Balanced (50/50) indicates bidirectional volatility - consider straddles instead of directional bets.";

export function SpikeDirectionBias({ data, testId }: SpikeDirectionBiasProps) {
  const { up_prob, down_prob } = data.spike_direction_bias;
  const upPercent = Math.round(up_prob * 100);
  const downPercent = Math.round(down_prob * 100);

  return (
    <TileWrapper title="Spike Direction Bias" helpText={helpText} testId={testId}>
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <div className="flex-1 text-right">
            <div className="text-xs text-muted-foreground mb-1">Downside</div>
            <div className="text-2xl font-bold font-mono text-bearish">
              {downPercent}%
            </div>
          </div>
          
          <div className="w-px h-16 bg-border" />
          
          <div className="flex-1 text-left">
            <div className="text-xs text-muted-foreground mb-1">Upside</div>
            <div className="text-2xl font-bold font-mono text-bullish">
              {upPercent}%
            </div>
          </div>
        </div>

        <div className="flex items-center gap-0.5 h-8 rounded-lg overflow-hidden">
          <div 
            className="h-full bg-bearish flex items-center justify-center transition-all duration-300"
            style={{ width: `${downPercent}%` }}
          >
            {downPercent > 15 && <ArrowDown className="h-4 w-4 text-bearish-foreground" />}
          </div>
          <div 
            className="h-full bg-bullish flex items-center justify-center transition-all duration-300"
            style={{ width: `${upPercent}%` }}
          >
            {upPercent > 15 && <ArrowUp className="h-4 w-4 text-bullish-foreground" />}
          </div>
        </div>

        <div className="text-center p-2 bg-muted rounded">
          <div className="text-xs text-muted-foreground">Directional Edge</div>
          <div className="text-sm font-semibold font-mono">
            {Math.abs(upPercent - downPercent)}% 
            <span className="text-xs ml-1">
              {upPercent > downPercent ? "(Bullish Bias)" : downPercent > upPercent ? "(Bearish Bias)" : "(Neutral)"}
            </span>
          </div>
        </div>
      </div>
    </TileWrapper>
  );
}
