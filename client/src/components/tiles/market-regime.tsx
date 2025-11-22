import { TileWrapper } from "./tile-wrapper";
import { MarketData } from "@shared/schema";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown, Minus, Activity } from "lucide-react";

interface MarketRegimeProps {
  data: MarketData;
  testId: string;
}

const helpText = "Market Regime classifies current market conditions combining price action and volatility. LOW_VOL_BULL: stable uptrend (ideal for selling puts). HIGH_VOL_BULL: volatile rally (caution). LOW_VOL_BEAR: steady decline (sell calls carefully). HIGH_VOL_BEAR: panic selling (avoid aggressive shorts). SIDEWAYS: range-bound (iron condors, strangles). CHOPPY: unpredictable (reduce exposure).";

export function MarketRegime({ data, testId }: MarketRegimeProps) {
  const getRegimeDetails = () => {
    const regime = data.regime;
    
    if (regime === "LOW_VOL_BULL") {
      return {
        label: "Low Vol Bull",
        description: "Stable uptrend",
        icon: <TrendingUp className="h-5 w-5" />,
        color: "bg-bullish text-bullish-foreground",
      };
    }
    if (regime === "HIGH_VOL_BULL") {
      return {
        label: "High Vol Bull",
        description: "Volatile rally",
        icon: <Activity className="h-5 w-5" />,
        color: "bg-spike text-spike-foreground",
      };
    }
    if (regime === "LOW_VOL_BEAR") {
      return {
        label: "Low Vol Bear",
        description: "Steady decline",
        icon: <TrendingDown className="h-5 w-5" />,
        color: "bg-bearish text-bearish-foreground",
      };
    }
    if (regime === "HIGH_VOL_BEAR") {
      return {
        label: "High Vol Bear",
        description: "Panic selling",
        icon: <Activity className="h-5 w-5" />,
        color: "bg-destructive text-destructive-foreground",
      };
    }
    if (regime === "SIDEWAYS") {
      return {
        label: "Sideways",
        description: "Range-bound",
        icon: <Minus className="h-5 w-5" />,
        color: "bg-neutral text-neutral-foreground",
      };
    }
    return {
      label: "Choppy",
      description: "Unpredictable",
      icon: <Activity className="h-5 w-5" />,
      color: "bg-muted text-muted-foreground",
    };
  };

  const details = getRegimeDetails();

  return (
    <TileWrapper title="Market Regime" helpText={helpText} testId={testId}>
      <div className="flex flex-col items-center gap-4 py-4">
        <div className={`flex items-center gap-3 px-6 py-4 rounded-lg ${details.color}`}>
          {details.icon}
          <span className="text-xl font-bold" data-testid={`text-regime-${testId}`}>{details.label}</span>
        </div>
        
        <div className="text-center">
          <div className="text-sm font-medium" data-testid={`text-regime-description-${testId}`}>{details.description}</div>
          <div className="text-xs text-muted-foreground mt-1">Current Market Classification</div>
        </div>
      </div>
    </TileWrapper>
  );
}
