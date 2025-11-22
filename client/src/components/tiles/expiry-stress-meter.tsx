import { TileWrapper } from "./tile-wrapper";
import { SellerBlock } from "@/lib/aegis-data";
import { Shield, AlertTriangle } from "lucide-react";

interface ExpiryStressMeterProps {
  data: SellerBlock;
  testId: string;
}

const helpText = "Expiry Stress Meter quantifies market tension approaching option expiry. Low stress (<30) suggests calm conditions ideal for aggressive selling. Medium (30-60) indicates normal caution. High stress (>60) warns of elevated gamma risk, pinning effects, and potential violent moves as positions unwind.";

export function ExpiryStressMeter({ data, testId }: ExpiryStressMeterProps) {
  const { score, label } = data.expiry_stress;

  const getColor = () => {
    if (label === "CALM") return { text: "text-bullish", bg: "bg-bullish/20", stroke: "stroke-bullish" };
    if (label === "CAUTION") return { text: "text-neutral", bg: "bg-neutral/20", stroke: "stroke-neutral" };
    return { text: "text-bearish", bg: "bg-bearish/20", stroke: "stroke-bearish" };
  };

  const colors = getColor();
  const circumference = 2 * Math.PI * 40;
  const offset = circumference - (score / 100) * circumference;

  return (
    <TileWrapper title="Expiry Stress Meter" helpText={helpText} testId={testId}>
      <div className="flex flex-col items-center gap-4">
        <div className="relative w-28 h-28">
          <svg className="transform -rotate-90 w-full h-full">
            <circle
              cx="56"
              cy="56"
              r="40"
              className="stroke-muted"
              strokeWidth="10"
              fill="none"
            />
            <circle
              cx="56"
              cy="56"
              r="40"
              className={colors.stroke}
              strokeWidth="10"
              fill="none"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              strokeLinecap="round"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            {label === "CALM" ? (
              <Shield className={`h-6 w-6 ${colors.text}`} />
            ) : (
              <AlertTriangle className={`h-6 w-6 ${colors.text}`} />
            )}
            <span className={`text-xl font-bold font-mono ${colors.text} mt-1`}>
              {score.toFixed(2)}
            </span>
          </div>
        </div>

        <div className={`px-4 py-2 rounded-lg ${colors.bg} ${colors.text} font-semibold`}>
          {label} Stress
        </div>

        <div className="text-xs text-muted-foreground text-center">
          Gamma Risk & Pinning Effect
        </div>
      </div>
    </TileWrapper>
  );
}
