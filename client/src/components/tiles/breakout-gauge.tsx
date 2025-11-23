import { TileWrapper } from "./tile-wrapper";
import { BuyerBlock } from "@/lib/aegis-data";
import { TrendingUp } from "lucide-react";

interface BreakoutGaugeProps {
  data: BuyerBlock;
  testId: string;
}

const helpText = "Breakout Potential measures today's probability of significant price movement beyond normal ranges. LOW (<40): theta decay dominates, avoid buying options. MODERATE (40-70): edge exists but selective. HIGH (>70): strong breakout setup, favorable for option buyers willing to pay premium.";

export function BreakoutGauge({ data, testId }: BreakoutGaugeProps) {
  const { score: rawScore, label } = data.breakout_today;
  const score = rawScore * 100;

  const getColor = () => {
    if (label === "HIGH") return { text: "text-spike", bg: "bg-spike/20", stroke: "stroke-spike" };
    if (label === "MEDIUM") return { text: "text-neutral", bg: "bg-neutral/20", stroke: "stroke-neutral" };
    return { text: "text-muted-foreground", bg: "bg-muted", stroke: "stroke-muted-foreground" };
  };

  const colors = getColor();
  const circumference = 2 * Math.PI * 45;
  const offset = circumference - (score / 100) * circumference;

  return (
    <TileWrapper title="Breakout Potential (Today)" helpText={helpText} testId={testId}>
      <div className="flex flex-col items-center gap-4">
        <div className="relative w-32 h-32">
          <svg className="transform -rotate-90 w-full h-full">
            <circle
              cx="64"
              cy="64"
              r="45"
              className="stroke-muted"
              strokeWidth="8"
              fill="none"
            />
            <circle
              cx="64"
              cy="64"
              r="45"
              className={colors.stroke}
              strokeWidth="8"
              fill="none"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              strokeLinecap="round"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <TrendingUp className={`h-6 w-6 ${colors.text} mb-1`} />
            <span className={`text-2xl font-bold font-mono ${colors.text}`} data-testid={`text-breakout-score-${testId}`}>
              {score.toFixed(2)}
            </span>
          </div>
        </div>

        <div className={`px-4 py-2 rounded-lg ${colors.bg} ${colors.text} font-semibold`} data-testid={`text-breakout-level-${testId}`}>
          {label} Potential
        </div>

        <div className="grid grid-cols-3 gap-2 w-full text-xs">
          <div className={`text-center p-2 rounded ${label === "LOW" ? "bg-muted text-foreground font-semibold" : "bg-muted/50 text-muted-foreground"}`}>
            Low
          </div>
          <div className={`text-center p-2 rounded ${label === "MEDIUM" ? "bg-neutral/20 text-neutral font-semibold" : "bg-muted/50 text-muted-foreground"}`}>
            Moderate
          </div>
          <div className={`text-center p-2 rounded ${label === "HIGH" ? "bg-spike/20 text-spike font-semibold" : "bg-muted/50 text-muted-foreground"}`}>
            High
          </div>
        </div>
      </div>
    </TileWrapper>
  );
}
