import { TileWrapper } from "./tile-wrapper";
import { SellerData } from "@shared/schema";
import { Zap } from "lucide-react";

interface VolatilityTrapProps {
  data: SellerData;
  testId: string;
}

const helpText = "Volatility Trap measures risk of sudden IV spike after selling options. Low (<30): premiums may be too thin but safe. Medium (30-60): balanced risk-reward. High (>60): tempting premiums but dangerous - IV could explode causing mark-to-market losses before expiry. Consider this before selling in apparently 'calm' markets.";

export function VolatilityTrap({ data, testId }: VolatilityTrapProps) {
  const { score, level } = data.trap;
  
  const getDetails = () => {
    if (level === "LOW") {
      return {
        color: "text-bullish",
        bg: "bg-bullish/10",
        label: "Safe - Low Trap Risk",
        icon: <Zap className="h-5 w-5 text-bullish" />,
      };
    }
    if (level === "MEDIUM") {
      return {
        color: "text-neutral",
        bg: "bg-neutral/10",
        label: "Caution - Moderate Risk",
        icon: <Zap className="h-5 w-5 text-neutral" />,
      };
    }
    return {
      color: "text-bearish",
      bg: "bg-bearish/10",
      label: "Danger - High Trap Risk",
      icon: <Zap className="h-5 w-5 text-bearish" />,
    };
  };

  const details = getDetails();

  return (
    <TileWrapper title="Volatility Trap" helpText={helpText} testId={testId}>
      <div className="space-y-4">
        <div className="flex flex-col items-center gap-3">
          <div className={`flex items-center justify-center w-16 h-16 rounded-full ${details.bg}`}>
            {details.icon}
          </div>
          <div className={`text-3xl font-bold font-mono ${details.color}`}>
            {score.toFixed(0)}
          </div>
        </div>

        <div className={`p-3 rounded-lg ${details.bg} text-center`}>
          <div className={`font-semibold ${details.color}`}>{details.label}</div>
        </div>

        <div className="space-y-1.5">
          <div className="flex justify-between text-xs">
            <span className="text-bullish">Safe</span>
            <span className="text-neutral">Caution</span>
            <span className="text-bearish">Danger</span>
          </div>
          <div className="h-2 rounded-full overflow-hidden flex">
            <div className="flex-1 bg-bullish/30" />
            <div className="flex-1 bg-neutral/30" />
            <div className="flex-1 bg-bearish/30" />
          </div>
          <div className="relative h-1">
            <div 
              className="absolute w-0.5 h-4 bg-foreground rounded-full -top-1.5"
              style={{ left: `${score}%` }}
            />
          </div>
        </div>
      </div>
    </TileWrapper>
  );
}
