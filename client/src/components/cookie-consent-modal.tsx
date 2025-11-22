import { useState, useEffect } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Cookie } from "lucide-react";

export function CookieConsentModal() {
  const [open, setOpen] = useState(false);
  const [analytics, setAnalytics] = useState(false);

  useEffect(() => {
    const consent = localStorage.getItem("aegis-cookie-consent");
    if (!consent) {
      setOpen(true);
    }
  }, []);

  const handleSave = () => {
    const consent = {
      analytics,
      timestamp: Date.now(),
    };
    localStorage.setItem("aegis-cookie-consent", JSON.stringify(consent));
    setOpen(false);
  };

  const handleAcceptAll = () => {
    setAnalytics(true);
    setTimeout(() => {
      const consent = {
        analytics: true,
        timestamp: Date.now(),
      };
      localStorage.setItem("aegis-cookie-consent", JSON.stringify(consent));
      setOpen(false);
    }, 100);
  };

  const handleRejectAll = () => {
    setAnalytics(false);
    setTimeout(() => {
      const consent = {
        analytics: false,
        timestamp: Date.now(),
      };
      localStorage.setItem("aegis-cookie-consent", JSON.stringify(consent));
      setOpen(false);
    }, 100);
  };

  if (!open) return null;

  return (
    <Dialog open={open} onOpenChange={() => {}}>
      <DialogContent className="sm:max-w-[500px]" hideClose data-testid="modal-cookie-consent">
        <DialogHeader>
          <div className="flex items-center gap-3 mb-2">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
              <Cookie className="h-6 w-6 text-primary" />
            </div>
            <DialogTitle className="text-xl">Cookies & Advertising Consent</DialogTitle>
          </div>
          <DialogDescription asChild className="text-left pt-4">
            <div className="space-y-4">
              <p className="text-sm leading-relaxed">
                We use cookies for theme preferences and performance. Our advertising partner (Adsterra) may also use cookies to show you relevant ads. You can control this below.
              </p>
              <div className="flex items-start space-x-3 rounded-lg border border-border p-4 hover-elevate">
                <Checkbox
                  id="analytics"
                  checked={analytics}
                  onCheckedChange={(checked) => setAnalytics(checked as boolean)}
                  data-testid="checkbox-analytics"
                />
                <div className="flex-1">
                  <Label htmlFor="analytics" className="font-semibold text-sm cursor-pointer">
                    Allow Analytics & Advertising (Adsterra)
                  </Label>
                  <p className="text-xs text-muted-foreground mt-1">
                    Helps us improve the dashboard and show relevant ads
                  </p>
                </div>
              </div>
              <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
                <a href="/privacy" className="hover:text-foreground underline">Privacy</a>
                <span>·</span>
                <a href="/cookies" className="hover:text-foreground underline">Cookies</a>
                <span>·</span>
                <a href="/terms" className="hover:text-foreground underline">Terms</a>
              </div>
            </div>
          </DialogDescription>
        </DialogHeader>
        <div className="flex flex-col sm:flex-row gap-2 mt-4">
          <Button onClick={handleAcceptAll} className="flex-1" data-testid="button-accept-all">
            Accept All
          </Button>
          <Button onClick={handleRejectAll} variant="outline" className="flex-1" data-testid="button-reject-all">
            Reject All
          </Button>
          <Button onClick={handleSave} variant="secondary" className="flex-1" data-testid="button-save-choices">
            Save Choices
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
