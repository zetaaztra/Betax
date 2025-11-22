import { ReactNode, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { HelpCircle } from "lucide-react";
import { TileHelpModal } from "../tile-help-modal";

interface TileWrapperProps {
  title: string;
  helpText: string;
  children: ReactNode;
  testId?: string;
  className?: string;
}

export function TileWrapper({ title, helpText, children, testId, className = "" }: TileWrapperProps) {
  const [showHelp, setShowHelp] = useState(false);

  return (
    <>
      <Card className={`hover-elevate transition-all duration-200 ${className}`} data-testid={testId}>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between gap-2">
            <CardTitle className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              {title}
            </CardTitle>
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6 shrink-0"
              onClick={() => setShowHelp(true)}
              data-testid={`button-help-${testId}`}
            >
              <HelpCircle className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>{children}</CardContent>
      </Card>
      <TileHelpModal
        open={showHelp}
        onClose={() => setShowHelp(false)}
        title={title}
        description={helpText}
      />
    </>
  );
}
