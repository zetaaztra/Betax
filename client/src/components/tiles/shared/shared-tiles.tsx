/**
 * Shared tile components used across tabs
 * Examples: risk score dial, mini sparkline, probability curve
 */

import React from 'react';

export function RiskScoreDial({ score }: { score: number }) {
  return (
    <div className="flex items-center justify-center">
      <div className="text-center">
        <div className="text-4xl font-bold text-red-500">{(score * 100).toFixed(0)}</div>
        <div className="text-xs text-muted-foreground">Risk Score</div>
      </div>
    </div>
  );
}

export function MiniSparkline({ values }: { values: number[] }) {
  return (
    <div className="flex items-end gap-1 h-12">
      {values.map((v, i) => (
        <div
          key={i}
          className="flex-1 bg-blue-500 rounded-sm"
          style={{ height: `${(v / Math.max(...values)) * 100}%` }}
        />
      ))}
    </div>
  );
}

export function ProbabilityCurve({ points }: { points: Array<{ x: number; y: number }> }) {
  return (
    <div className="w-full h-24 bg-muted rounded">
      {/* TODO: Use recharts or similar to render curve */}
      <p className="text-xs text-muted-foreground p-2">Probability Distribution</p>
    </div>
  );
}
