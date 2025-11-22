import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { RefreshCw, Moon, Sun } from "lucide-react";
import { DirectionView } from "./direction-view";
import { SellerView } from "./seller-view";
import { BuyerView } from "./buyer-view";
import { ConcentricBackground } from "@/components/concentric-background";
import { DisclaimerModal } from "@/components/disclaimer-modal";
import { CookieConsentModal } from "@/components/cookie-consent-modal";
import { HowToUse } from "@/components/how-to-use";
import { Footer } from "@/components/footer";
import { useTheme } from "@/components/theme-provider";
import { AegisMatrixData } from "@shared/schema";

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<"direction" | "seller" | "buyer">("direction");
  const { theme, setTheme } = useTheme();

  const { data, isLoading, refetch } = useQuery<AegisMatrixData>({
    queryKey: ["/api/aegismatrix"],
  });

  const handleRefresh = () => {
    window.location.reload();
  };

  return (
    <div className="min-h-screen flex flex-col bg-background text-foreground relative overflow-x-hidden">
      <ConcentricBackground />

      <header className="relative z-10 border-b border-border bg-card/95 backdrop-blur supports-[backdrop-filter]:bg-card/80">
        <div className="mx-auto max-w-7xl px-6 py-6">
          <div className="flex flex-col gap-4">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl md:text-3xl font-bold">Tradyxa Aegis Matrix</h1>
                <p className="text-sm text-muted-foreground mt-1">
                  NIFTY Options Intelligence System Using Trained ML Models
                </p>
              </div>

              <div className="flex items-center gap-2">
                <div className="hidden md:block text-right mr-2">
                  <p className="text-xs text-muted-foreground font-medium">Last Updated</p>
                  <p className="text-xs text-muted-foreground">M-F 09:15-15:30 IST (30m)</p>
                </div>
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
                  data-testid="button-theme-toggle"
                >
                  {theme === "dark" ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
                </Button>

                <Button
                  variant="outline"
                  onClick={handleRefresh}
                  data-testid="button-refresh"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Refresh
                </Button>
              </div>
            </div>

            <div className="flex flex-col md:flex-row md:items-center gap-2">
              <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as typeof activeTab)} className="w-full md:w-auto">
                <TabsList className="grid w-full md:w-auto md:inline-grid grid-cols-3">
                  <TabsTrigger value="direction" data-testid="tab-direction">
                    Direction
                  </TabsTrigger>
                  <TabsTrigger value="buyer" data-testid="tab-buyer">
                    Option Buyers
                  </TabsTrigger>
                  <TabsTrigger value="seller" data-testid="tab-seller">
                    Option Sellers
                  </TabsTrigger>
                </TabsList>
              </Tabs>
              <span className="text-xs text-muted-foreground ml-2 hidden md:inline-block animate-pulse">
                Click tabs to change views
              </span>
            </div>
          </div>
        </div>
      </header>

      <main className="relative z-10 flex-1">
        <Tabs value={activeTab} className="h-full">
          <TabsContent value="direction" className="m-0">
            <DirectionView data={data} />
          </TabsContent>
          <TabsContent value="buyer" className="m-0">
            <BuyerView data={data} />
          </TabsContent>
          <TabsContent value="seller" className="m-0">
            <SellerView data={data} />
          </TabsContent>
        </Tabs>
      </main>

      <HowToUse />
      <Footer />

      <DisclaimerModal />
      <CookieConsentModal />
    </div>
  );
}
