import { TileWrapper } from "./tile-wrapper";
import { SellerData } from "@shared/schema";
import { Flag } from "lucide-react";

interface SellerDailyFlagProps {
  data: SellerData;
  testId: string;
}

const helpText = "Seller Daily Flag provides a quick go/no-go signal for aggressive short selling today. FAVOURABLE: all conditions aligned for selling premium. NEUTRAL: mixed signals, proceed with standard caution. RISKY: multiple red flags present, avoid aggressive new positions or reduce existing exposure.";

export function SellerDailyFlag({ data, testId }: SellerDailyFlagProps) {
  const getDetails = () => {
    if (data.daily_flag === "FAVOURABLE") {
      return {
        label: "Favourable",
        description: "Green Light for Selling",
        icon: <Flag className="h-6 w-6" />,
        color: "bg-bullish text-bullish-foreground",
      };
    }
    if (data.daily_flag === "NEUTRAL") {
      return {
        label: "Neutral",
        description: "Standard Caution",
        icon: <Flag className="h-6 w-6" />,
        color: "bg-neutral text-neutral-foreground",
      };
    }
    return {
      label: "Risky",
      description: "Avoid Aggressive Shorting",
      icon: <Flag className="h-6 w-6" />,
      color: "bg-bearish text-bearish-foreground",
    };
  };

  const details = getDetails();

  return (
    <TileWrapper title="Seller Daily Flag" helpText={helpText} testId={testId}>
      <div className="flex flex-col items-center gap-4 py-4">
        <div className={`flex flex-col items-center gap-3 px-8 py-6 rounded-lg ${details.color}`}>
          {details.icon}
          <span className="text-2xl font-bold" data-testid={`text-daily-flag-${testId}`}>{details.label}</span>
        </div>
        
        <div className="text-center">
          <div className="text-sm font-medium" data-testid={`text-daily-flag-description-${testId}`}>{details.description}</div>
          <div className="text-xs text-muted-foreground mt-1">Today's Recommendation</div>
        </div>
      </div>
    </TileWrapper>
  );
}
