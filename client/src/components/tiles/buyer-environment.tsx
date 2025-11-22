import { TileWrapper } from "./tile-wrapper";
import { BuyerData } from "@shared/schema";
import { ThumbsUp, AlertCircle, XCircle } from "lucide-react";

interface BuyerEnvironmentProps {
  data: BuyerData;
  testId: string;
}

const helpText = "Buyer Environment State synthesizes breakout potential, theta-edge, and regime into actionable guidance. PREMIUM_FRIENDLY: conditions favor option buying, multiple edges aligned. CAUTIOUS: mixed signals, be selective. AVOID_FULL_RISK: hostile conditions, theta burn likely exceeds gains - stay out or use spreads to cap premium cost.";

export function BuyerEnvironment({ data, testId }: BuyerEnvironmentProps) {
  const getDetails = () => {
    if (data.environment_state === "PREMIUM_FRIENDLY") {
      return {
        label: "Premium-Friendly",
        description: "Favorable for Buyers",
        icon: <ThumbsUp className="h-6 w-6" />,
        color: "bg-spike text-spike-foreground",
      };
    }
    if (data.environment_state === "CAUTIOUS") {
      return {
        label: "Cautious",
        description: "Be Selective",
        icon: <AlertCircle className="h-6 w-6" />,
        color: "bg-neutral text-neutral-foreground",
      };
    }
    return {
      label: "Avoid Full Risk",
      description: "Hostile Conditions",
      icon: <XCircle className="h-6 w-6" />,
      color: "bg-bearish text-bearish-foreground",
    };
  };

  const details = getDetails();

  return (
    <TileWrapper title="Buyer Environment State" helpText={helpText} testId={testId}>
      <div className="flex flex-col items-center gap-4 py-4">
        <div className={`flex flex-col items-center gap-3 px-8 py-6 rounded-lg ${details.color}`}>
          {details.icon}
          <span className="text-2xl font-bold text-center">{details.label}</span>
        </div>
        
        <div className="text-center">
          <div className="text-sm font-medium">{details.description}</div>
          <div className="text-xs text-muted-foreground mt-1">Today's Environment</div>
        </div>
      </div>
    </TileWrapper>
  );
}
