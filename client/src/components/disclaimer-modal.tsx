import { useState, useEffect } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { AlertTriangle } from "lucide-react";

export function DisclaimerModal() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const lastShown = localStorage.getItem("aegis-disclaimer-shown");
    const now = Date.now();
    const twoDays = 2 * 24 * 60 * 60 * 1000;

    if (!lastShown || now - parseInt(lastShown) > twoDays) {
      setOpen(true);
    }
  }, []);

  const handleAccept = () => {
    localStorage.setItem("aegis-disclaimer-shown", Date.now().toString());
    setOpen(false);
  };

  return (
    <Dialog open={open} onOpenChange={() => { }}>
      <DialogContent className="sm:max-w-[500px]" hideClose data-testid="modal-disclaimer">
        <DialogHeader>
          <div className="flex items-center gap-3 mb-2">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-destructive/10">
              <AlertTriangle className="h-6 w-6 text-destructive" />
            </div>
            <DialogTitle className="text-xl">Important Disclaimer</DialogTitle>
          </div>
          <DialogDescription asChild className="text-left pt-4">
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                <strong className="font-semibold text-foreground">Educational Use Only:</strong> Tradyxa Aegis Matrix is designed for educational and informational purposes. This tool does not provide financial advice.
              </p>
              <p className="text-sm leading-relaxed">
                <strong className="font-semibold text-foreground">No Trading Recommendations:</strong> Nothing displayed on this dashboard constitutes a recommendation to buy, sell, or hold any securities or derivatives.
              </p>
              <p className="text-sm leading-relaxed">
                <strong className="font-semibold text-foreground">Risk Awareness:</strong> Options trading involves substantial risk and is not suitable for all investors. You may lose your entire investment.
              </p>
              <p className="text-sm leading-relaxed">
                <strong className="font-semibold text-foreground">Independent Decision:</strong> Any trading decisions you make are solely your responsibility. Consult a licensed financial advisor before making investment decisions.
              </p>
              <p className="text-xs text-muted-foreground mt-4">
                By clicking "I Understand", you acknowledge that you have read and understood this disclaimer.
              </p>
            </div>
          </DialogDescription>
        </DialogHeader>
        <div className="flex justify-end mt-4">
          <Button onClick={handleAccept} size="lg" className="w-full sm:w-auto" data-testid="button-accept-disclaimer">
            I Understand
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
