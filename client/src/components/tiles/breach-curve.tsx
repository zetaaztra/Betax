import { TileWrapper } from "./tile-wrapper";
import { SellerBlock } from "@/lib/aegis-data";

interface BreachCurveProps {
  data: SellerBlock;
  testId: string;
}

const helpText = "Range Breach Curve plots probability of NIFTY moving X points away from current spot before expiry. Steeper curve = lower breach risk (good for sellers). Flatter curve = higher breach probability (risky). Use this to size your strikes: sell further OTM if curve is steep, closer if flat for balanced risk.";

export function BreachCurve({ data, testId }: BreachCurveProps) {
  const breachData = data.breach_probabilities;

  return (
    <TileWrapper title="Range Breach Curve" helpText={helpText} testId={testId}>
      <div className="space-y-4">
        <div className="h-32 relative">
          <svg className="w-full h-full overflow-visible" viewBox="0 0 300 130">
            <defs>
              <linearGradient id="breachGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="rgb(var(--bearish))" stopOpacity="0.3" />
                <stop offset="100%" stopColor="rgb(var(--bearish))" stopOpacity="0.05" />
              </linearGradient>
            </defs>

            <path
              d={`M 0 ${125 - breachData[0].probability * 100} ${breachData.map((d, i) => {
                const x = (i / (breachData.length - 1)) * 300;
                const y = 125 - d.probability * 100;
                return `L ${x} ${y}`;
              }).join(" ")} L 300 125 L 0 125 Z`}
              fill="url(#breachGradient)"
              stroke="hsl(var(--bearish))"
              strokeWidth="2"
            />

            {breachData.map((d, i) => {
              const x = (i / (breachData.length - 1)) * 300;
              const y = 120 - d.probability * 100;
              return (
                <circle
                  key={i}
                  cx={x}
                  cy={y}
                  r="3"
                  fill="hsl(var(--bearish))"
                />
              );
            })}
          </svg>
        </div>

        <div className="grid grid-cols-4 gap-2 text-xs">
          {breachData.map((d, i) => (
            <div key={i} className="text-center">
              <div className="text-muted-foreground">{d.distance} pts</div>
              <div className="font-semibold font-mono text-bearish">
                {(d.probability * 100).toFixed(2)}%
              </div>
            </div>
          ))}
        </div>
      </div>
    </TileWrapper>
  );
}
