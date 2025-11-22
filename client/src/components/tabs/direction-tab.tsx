/**
 * Direction Tab Component
 * Displays: today direction, horizon forecasts (t+1 to t+40), risk score
 */

import React from 'react';
import { Card } from '@/components/ui/card';

export function DirectionTab() {
  return (
    <div className="space-y-4">
      <Card className="p-6">
        <h2 className="text-2xl font-bold mb-4">Direction Forecasts</h2>
        {/* TODO: Load data from aegismatrix.json */}
        {/* Display today, horizons (t1-t40), risk score */}
        <p className="text-muted-foreground">Today Direction Tile</p>
      </Card>
    </div>
  );
}
