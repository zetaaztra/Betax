import { TileWrapper } from "./tile-wrapper";
import { BuyerData } from "@shared/schema";
import { Clock, Zap } from "lucide-react";

interface ThetaEdgeScoreProps {
  data: BuyerData;
  testId: string;
}

const helpText = "Theta vs Edge Score answers: 'Is the potential move large enough to justify paying premium?' POOR (<40): theta decay kills profits, don't buy. FAIR (40-65): marginal edge, only for high conviction trades. GOOD (>65): expected movement exceeds theta cost, favorable buying opportunity.";

export function ThetaEdgeScore({ data, testId }: ThetaEdgeScoreProps) {
  const { score, level } = data.theta_edge;
  
  const getDetails = () => {
    if (level === "GOOD") {
      return {
        label: "Good",
        description: "Edge Justifies Premium",
        icon: <Zap className="h-5 w-5 text-spike" />,
        color: "text-spike",
        bg: "bg-spike/10",
      };
    }
    if (level === "FAIR") {
      return {
        label: "Fair",
        description: "Marginal Edge",
        icon: <Clock className="h-5 w-5 text-neutral" />,
        color: "text-neutral",
        bg: "bg-neutral/10",
      };
    }
    return {
      label: "Poor",
      description: "Don't Waste Premium",
      icon: <Clock className="h-5 w-5 text-muted-foreground" />,
      color: "text-muted-foreground",
      bg: "bg-muted",
    };
  };

  const details = getDetails();
  const position = score;

  return (
    <TileWrapper title="Theta vs Edge Score" helpText={helpText} testId={testId}>
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
          <div className="text-xs text-muted-foreground mt-1">{details.description}</div>
        </div>

        <div className="space-y-1.5">
          <div className="flex justify-between text-xs">
            <span className="text-muted-foreground">Poor</span>
            <span className="text-neutral">Fair</span>
            <span className="text-spike">Good</span>
          </div>
          <div className="h-2 rounded-full overflow-hidden flex">
            <div className="flex-1 bg-muted" />
            <div className="flex-1 bg-neutral/30" />
            <div className="flex-1 bg-spike/30" />
          </div>
          <div className="relative h-1">
            <div 
              className="absolute w-0.5 h-4 bg-foreground rounded-full -top-1.5"
              style={{ left: `${position}%` }}
            />
          </div>
        </div>
      </div>
    </TileWrapper>
  );
}
