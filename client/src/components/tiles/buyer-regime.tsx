import { TileWrapper } from "./tile-wrapper";
import { BuyerData } from "@shared/schema";
import { TrendingUp, Activity, Minus } from "lucide-react";

interface BuyerRegimeProps {
  data: BuyerData;
  testId: string;
}

const helpText = "Buyer Regime categorizes market behavior for option buyer strategies. TREND_FOLLOWING: strong directional momentum, buy directional options (calls in uptrend, puts in downtrend). MEAN_REVERTING: buy at extremes, fade moves. CHOPPY: avoid buying, theta decay dominates in indecisive markets.";

export function BuyerRegime({ data, testId }: BuyerRegimeProps) {
  const getDetails = () => {
    if (data.regime === "TREND_FOLLOWING") {
      return {
        label: "Trend Following",
        description: "Directional Momentum",
        icon: <TrendingUp className="h-6 w-6" />,
        color: "bg-spike text-spike-foreground",
      };
    }
    if (data.regime === "MEAN_REVERTING") {
      return {
        label: "Mean Reverting",
        description: "Buy at Extremes",
        icon: <Activity className="h-6 w-6" />,
        color: "bg-neutral text-neutral-foreground",
      };
    }
    return {
      label: "Choppy",
      description: "Avoid Buying",
      icon: <Minus className="h-6 w-6" />,
      color: "bg-muted text-muted-foreground",
    };
  };

  const details = getDetails();

  return (
    <TileWrapper title="Buyer Regime" helpText={helpText} testId={testId}>
      <div className="flex flex-col items-center gap-4 py-4">
        <div className={`flex items-center gap-3 px-6 py-4 rounded-lg ${details.color}`}>
          {details.icon}
          <span className="text-xl font-bold">{details.label}</span>
        </div>
        
        <div className="text-center">
          <div className="text-sm font-medium">{details.description}</div>
          <div className="text-xs text-muted-foreground mt-1">Current Buyer Environment</div>
        </div>

        <div className="grid grid-cols-3 gap-2 w-full text-xs">
          <div className={`text-center p-2 rounded ${data.regime === "TREND_FOLLOWING" ? "bg-spike/20 text-spike font-semibold" : "bg-muted/50 text-muted-foreground"}`}>
            Trend
          </div>
          <div className={`text-center p-2 rounded ${data.regime === "MEAN_REVERTING" ? "bg-neutral/20 text-neutral font-semibold" : "bg-muted/50 text-muted-foreground"}`}>
            Mean Rev
          </div>
          <div className={`text-center p-2 rounded ${data.regime === "CHOPPY" ? "bg-muted text-foreground font-semibold" : "bg-muted/50 text-muted-foreground"}`}>
            Choppy
          </div>
        </div>
      </div>
    </TileWrapper>
  );
}
