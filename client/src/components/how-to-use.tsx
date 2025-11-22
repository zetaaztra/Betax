import { useState } from "react";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { Button } from "@/components/ui/button";
import { ChevronDown, ChevronUp, BookOpen } from "lucide-react";

export function HowToUse() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="border-t border-border bg-card">
      <div className="mx-auto max-w-7xl px-6 py-8">
        <Collapsible open={isOpen} onOpenChange={setIsOpen}>
          <CollapsibleTrigger asChild>
            <Button
              variant="ghost"
              className="w-full flex items-center justify-between hover-elevate"
              data-testid="button-how-to-use"
            >
              <div className="flex items-center gap-2">
                <BookOpen className="h-5 w-5" />
                <span className="text-lg font-semibold">How to Use This Dashboard</span>
              </div>
              {isOpen ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
            </Button>
          </CollapsibleTrigger>
          <CollapsibleContent className="pt-6">
            <div className="grid md:grid-cols-3 gap-6">
              <div className="space-y-3">
                <h3 className="text-sm font-semibold uppercase tracking-wide text-primary">Direction Tab</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  View NIFTY's expected directional movement across multiple time horizons (today through next month). 
                  Use today's direction for intraday trades, longer horizons for position planning. Check risk score 
                  and market regime for overall context.
                </p>
              </div>
              
              <div className="space-y-3">
                <h3 className="text-sm font-semibold uppercase tracking-wide text-bullish">Option Sellers Tab</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  Identify safe zones for selling options (strangles, iron condors). Focus on safe range, 
                  expiry stress, and volatility trap before entering shorts. Seller regime tells you if 
                  conditions are calm, cautious, or hostile.
                </p>
              </div>
              
              <div className="space-y-3">
                <h3 className="text-sm font-semibold uppercase tracking-wide text-spike">Option Buyers Tab</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  Assess whether buying options is justified today. Breakout potential and theta-edge score 
                  tell you if premium cost is worth it. Use spike direction bias to choose calls vs puts, 
                  and gamma windows for intraday timing.
                </p>
              </div>
            </div>

            <div className="mt-6 p-4 bg-muted/50 rounded-lg">
              <h4 className="text-sm font-semibold mb-2">General Tips</h4>
              <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
                <li>Click the <span className="text-foreground">?</span> icon on any tile for detailed explanations</li>
                <li>Use the theme toggle for comfortable viewing in different lighting conditions</li>
                <li>Refresh button reloads all market data for latest analysis</li>
                <li>All data is for educational purposes - not financial advice</li>
              </ul>
            </div>
          </CollapsibleContent>
        </Collapsible>
      </div>
    </div>
  );
}
