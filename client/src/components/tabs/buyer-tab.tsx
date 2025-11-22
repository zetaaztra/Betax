/**
 * Buyer Tab Component
 * Displays: breakout today/next, spike direction, gamma windows, theta edge, buyer environment
 */

import React from 'react';
import { Card } from '@/components/ui/card';

export function BuyerTab() {
  return (
    <div className="space-y-4">
      <Card className="p-6">
        <h2 className="text-2xl font-bold mb-4">Option Buyers (PulseWave)</h2>
        {/* TODO: Load data from aegismatrix.json */}
        {/* Display breakout scores, spike bias, gamma windows, theta edge, buyer environment */}
        <p className="text-muted-foreground">Buyer Metrics</p>
      </Card>
    </div>
  );
}
