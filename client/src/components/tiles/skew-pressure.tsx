import { TileWrapper } from "./tile-wrapper";
import { SellerBlock } from "@/lib/aegis-data";

interface SkewPressureProps {
  data: SellerBlock;
  testId: string;
}

const helpText = "Skew Pressure shows relative demand for puts vs calls through implied volatility differentials. High put skew (left bar taller) indicates fear - market paying premium for downside protection. High call skew (right bar taller) suggests upside chasing. Balanced skew indicates neutral sentiment. Use this to identify which side to sell.";

export function SkewPressure({ data, testId }: SkewPressureProps) {
  const { put_skew, call_skew } = data.skew;
  const maxSkew = Math.max(Math.abs(put_skew), Math.abs(call_skew));
  const putHeight = (Math.abs(put_skew) / maxSkew) * 100;
  const callHeight = (Math.abs(call_skew) / maxSkew) * 100;

  return (
    <TileWrapper title="Skew Pressure (Calls vs Puts)" helpText={helpText} testId={testId}>
      <div className="space-y-4">
        <div className="flex items-end justify-center gap-8 h-32">
          <div className="flex flex-col items-center gap-2 flex-1 h-full">
            <div className="text-xs text-muted-foreground">Put Skew</div>
            <div className="flex-1 flex flex-col justify-end w-full">
              <div
                className="w-full bg-bearish/40 rounded-t-lg transition-all duration-300"
                style={{ height: `${putHeight}%` }}
              />
            </div>
            <div className="text-lg font-bold font-mono text-bearish">
              {put_skew.toFixed(3)}
            </div>
          </div>

          <div className="flex flex-col items-center gap-2 flex-1 h-full">
            <div className="text-xs text-muted-foreground">Call Skew</div>
            <div className="flex-1 flex flex-col justify-end w-full">
              <div
                className="w-full bg-bullish/40 rounded-t-lg transition-all duration-300"
                style={{ height: `${callHeight}%` }}
              />
            </div>
            <div className="text-lg font-bold font-mono text-bullish">
              {call_skew.toFixed(3)}
            </div>
          </div>
        </div>

        <div className="text-center p-2 bg-muted rounded">
          <div className="text-xs text-muted-foreground">Skew Differential</div>
          <div className="text-sm font-semibold font-mono">
            {Math.abs(put_skew - call_skew).toFixed(3)}
            <span className="text-xs ml-1">
              ({put_skew > call_skew ? "Put Heavy" : call_skew > put_skew ? "Call Heavy" : "Balanced"})
            </span>
          </div>
        </div>
      </div>
    </TileWrapper>
  );
}
