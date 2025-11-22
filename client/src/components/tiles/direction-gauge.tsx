import { TileWrapper } from "./tile-wrapper";
import { HorizonData } from "@shared/schema";
import { TrendingUp, TrendingDown, Minus, ArrowUp, ArrowDown } from "lucide-react";

interface DirectionGaugeProps {
  data: HorizonData;
  title: string;
  testId: string;
}

const helpTexts: Record<string, string> = {
  "Today Direction": "Shows the expected intraday direction for NIFTY based on current market conditions and technical analysis. UP indicates bullish momentum, DOWN indicates bearish pressure, NEUTRAL suggests range-bound movement. The expected move shows approximate points of movement.",
  "Tomorrow (T+1)": "1-day ahead directional forecast. Helps plan overnight positions and next-day strategies.",
  "Next 3 Days (T+3)": "3-day directional outlook. Useful for short-term swing trades and option expiry planning.",
  "This Week (T+5)": "5-day weekly directional bias. Guides weekly option strategies and position sizing.",
  "Next Week (T+10)": "10-day extended forecast. Helps identify medium-term trend alignment.",
  "This Month (T+20)": "20-day monthly directional view. Supports monthly option selection and portfolio rebalancing.",
  "Next Month (T+40)": "40-day long-term directional assessment. Assists with strategic positioning and risk management.",
};

export function DirectionGauge({ data, title, testId }: DirectionGaugeProps) {
  const getDirectionColor = () => {
    if (data.direction === "UP") return "text-bullish";
    if (data.direction === "DOWN") return "text-bearish";
    return "text-neutral";
  };

  const getDirectionBg = () => {
    if (data.direction === "UP") return "bg-bullish/10";
    if (data.direction === "DOWN") return "bg-bearish/10";
    return "bg-neutral/10";
  };

  const getDirectionIcon = () => {
    if (data.direction === "UP") return <TrendingUp className="h-5 w-5" />;
    if (data.direction === "DOWN") return <TrendingDown className="h-5 w-5" />;
    return <Minus className="h-5 w-5" />;
  };

  const convictionPercent = Math.round(data.conviction * 100);

  return (
    <TileWrapper title={title} helpText={helpTexts[title] || ""} testId={testId}>
      <div className="space-y-4">
        <div className="flex items-center justify-center">
          <div className={`flex flex-col items-center gap-2 p-6 rounded-lg ${getDirectionBg()}`}>
            <div className={`${getDirectionColor()}`}>
              {getDirectionIcon()}
            </div>
            <div className={`text-3xl font-bold font-mono ${getDirectionColor()}`} data-testid={`text-direction-${testId}`}>
              {data.direction}
            </div>
          </div>
        </div>
        
        <div className="space-y-2">
          <div className="flex justify-between items-baseline">
            <span className="text-sm text-muted-foreground">Expected Move</span>
            <span className={`text-2xl font-bold font-mono ${getDirectionColor()}`} data-testid={`text-expected-move-${testId}`}>
              {data.expected_move_points > 0 ? "+" : ""}{data.expected_move_points.toFixed(1)}
              <span className="text-sm ml-1">pts</span>
            </span>
          </div>
          
          <div>
            <div className="flex justify-between items-baseline mb-1">
              <span className="text-xs text-muted-foreground">Conviction</span>
              <span className="text-sm font-semibold font-mono" data-testid={`text-conviction-${testId}`}>{convictionPercent}%</span>
            </div>
            <div className="h-2 bg-muted rounded-full overflow-hidden">
              <div 
                className={`h-full ${data.direction === "UP" ? "bg-bullish" : data.direction === "DOWN" ? "bg-bearish" : "bg-neutral"}`}
                style={{ width: `${convictionPercent}%` }}
                data-testid={`bar-conviction-${testId}`}
              />
            </div>
          </div>
        </div>
      </div>
    </TileWrapper>
  );
}
