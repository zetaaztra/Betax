/**
 * Seller Tab Component
 * Displays: safe range, max pain, trap risk, skew, expiry stress, breach probabilities, seller flag
 */

import React from 'react';
import { Card } from '@/components/ui/card';

export function SellerTab() {
  return (
    <div className="space-y-4">
      <Card className="p-6">
        <h2 className="text-2xl font-bold mb-4">Option Sellers (RangeShield)</h2>
        {/* TODO: Load data from aegismatrix.json */}
        {/* Display safe range, trap risk, skew, expiry stress, breach curve, seller flag */}
        <p className="text-muted-foreground">Seller Metrics</p>
      </Card>
    </div>
  );
}
