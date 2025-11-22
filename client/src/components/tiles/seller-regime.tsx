import { TileWrapper } from "./tile-wrapper";
import { SellerData } from "@shared/schema";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, AlertCircle, XCircle } from "lucide-react";

interface SellerRegimeProps {
  data: SellerData;
  testId: string;
}

const helpText = "Seller Regime synthesizes stress, trap risk, and market conditions into trading environment classification. CALM: ideal for aggressive short selling, low risk. CAUTIOUS: moderate conditions, reduce position size. HOSTILE: dangerous environment, avoid new shorts or close existing positions to preserve capital.";

export function SellerRegime({ data, testId }: SellerRegimeProps) {
  const getDetails = () => {
    if (data.regime === "CALM") {
      return {
        label: "Calm",
        description: "Ideal for Sellers",
        icon: <CheckCircle2 className="h-6 w-6" />,
        color: "bg-bullish text-bullish-foreground",
      };
    }
    if (data.regime === "CAUTIOUS") {
      return {
        label: "Cautious",
        description: "Reduce Position Size",
        icon: <AlertCircle className="h-6 w-6" />,
        color: "bg-neutral text-neutral-foreground",
      };
    }
    return {
      label: "Hostile",
      description: "Avoid New Shorts",
      icon: <XCircle className="h-6 w-6" />,
      color: "bg-bearish text-bearish-foreground",
    };
  };

  const details = getDetails();

  return (
    <TileWrapper title="Seller Regime Tag" helpText={helpText} testId={testId}>
      <div className="flex flex-col items-center gap-4 py-4">
        <div className={`flex items-center gap-3 px-6 py-4 rounded-lg ${details.color}`}>
          {details.icon}
          <span className="text-xl font-bold">{details.label}</span>
        </div>
        
        <div className="text-center">
          <div className="text-sm font-medium">{details.description}</div>
          <div className="text-xs text-muted-foreground mt-1">Current Seller Environment</div>
        </div>

        <div className="grid grid-cols-3 gap-2 w-full text-xs">
          <div className={`text-center p-2 rounded ${data.regime === "CALM" ? "bg-bullish/20 text-bullish font-semibold" : "bg-muted text-muted-foreground"}`}>
            Calm
          </div>
          <div className={`text-center p-2 rounded ${data.regime === "CAUTIOUS" ? "bg-neutral/20 text-neutral font-semibold" : "bg-muted text-muted-foreground"}`}>
            Cautious
          </div>
          <div className={`text-center p-2 rounded ${data.regime === "HOSTILE" ? "bg-bearish/20 text-bearish font-semibold" : "bg-muted text-muted-foreground"}`}>
            Hostile
          </div>
        </div>
      </div>
    </TileWrapper>
  );
}
