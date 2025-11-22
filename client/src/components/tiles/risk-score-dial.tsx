import { TileWrapper } from "./tile-wrapper";
import { Shield } from "lucide-react";

interface RiskScoreDialProps {
  score: number;
  testId: string;
}

const helpText = "Overall directional risk score combines multiple factors: volatility, trend strength, breadth, and technical indicators. Lower scores (0-0.3) suggest stable conditions. Medium (0.3-0.6) indicates moderate uncertainty. High (0.6-1.0) warns of elevated risk requiring defensive positioning.";

export function RiskScoreDial({ score, testId }: RiskScoreDialProps) {
  const percentage = Math.round(score * 100);
  
  const getLevel = () => {
    if (score < 0.3) return { label: "Low Risk", color: "text-bullish", stroke: "stroke-bullish" };
    if (score < 0.6) return { label: "Moderate Risk", color: "text-neutral", stroke: "stroke-neutral" };
    return { label: "High Risk", color: "text-bearish", stroke: "stroke-bearish" };
  };

  const level = getLevel();
  const circumference = 2 * Math.PI * 45;
  const offset = circumference - (score * circumference);

  return (
    <TileWrapper title="Direction Risk Score" helpText={helpText} testId={testId}>
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
              className={level.stroke}
              strokeWidth="8"
              fill="none"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              strokeLinecap="round"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <Shield className={`h-6 w-6 ${level.color} mb-1`} />
            <span className={`text-2xl font-bold font-mono ${level.color}`} data-testid={`text-risk-score-${testId}`}>
              {percentage}
            </span>
          </div>
        </div>

        <div className="text-center">
          <div className={`font-semibold ${level.color}`} data-testid={`text-risk-level-${testId}`}>{level.label}</div>
          <div className="text-xs text-muted-foreground mt-1">Composite Risk Metric</div>
        </div>
      </div>
    </TileWrapper>
  );
}
