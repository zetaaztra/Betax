import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import { Link } from "wouter";

export default function Disclaimer() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="mx-auto max-w-3xl px-6 py-12">
        <Link href="/">
          <a className="inline-flex items-center text-primary hover:underline mb-6 text-sm font-medium transition-colors">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Dashboard
          </a>
        </Link>
        <h1 className="text-3xl font-bold mb-2">Disclaimer</h1>
        <p className="text-muted-foreground mb-8">Educational and informational use only. Not financial advice.</p>

        <div className="space-y-8">
          <section>
            <h2 className="text-xl font-semibold mb-3">Educational Purpose Only</h2>
            <p className="text-muted-foreground leading-relaxed">
              The information, analytics, indicators, models, forecasts, and visualizations on this website are provided solely for educational and informational purposes. Nothing here constitutes financial, investment, trading, tax, accounting, or legal advice.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3">SEBI Notice</h2>
            <p className="text-muted-foreground leading-relaxed">
              Zeta Aztra Technologies, its owner(s), developers, and affiliates are not SEBI-registered investment advisers or research analysts. All trading and investment decisions made based on the information presented here are taken entirely at the user's own risk.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3">Liability Disclaimer</h2>
            <p className="text-muted-foreground leading-relaxed">
              We explicitly disclaim any and all liability for losses, damages, or other consequences arising from use of, reliance upon, or inability to use the content, data, indicators, or models on this website. Users should consider consulting a SEBI-registered financial adviser.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3">Third-Party Content</h2>
            <p className="text-muted-foreground leading-relaxed">
              This website may display advertisements and links to external websites. Zeta Aztra Technologies does not endorse or control third-party content or claims, and assumes no responsibility for any products, services, or information provided by third parties. Interactions with such content are at your own discretion and risk.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3">Data Accuracy</h2>
            <p className="text-muted-foreground leading-relaxed">
              Market data and prices are sourced from publicly available providers (e.g., Yahoo Finance, NSE India). While reasonable efforts are made to ensure accuracy and timely updates, no guarantee or warranty is given regarding completeness, reliability, timeliness, suitability, or availability for any purpose. Market data may be delayed up to 30 minutes. For educational use only.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3">User Acknowledgment</h2>
            <p className="text-muted-foreground leading-relaxed">
              By using this website, you acknowledge and agree that you bear full responsibility for your trading and investment decisions, and that Zeta Aztra Technologies and contributors shall have no liability whatsoever for any loss or damage that may result.
            </p>
          </section>

          <div className="pt-8 border-t border-border mt-8">
            <p className="text-sm text-muted-foreground italic">
              Affiliation Disclaimer: Tradyxa Aegis Matrix is a product of Zeta Aztra Technologies (India) and is not affiliated with any other Tradyxa-named companies or domains.
            </p>
            <p className="text-sm text-muted-foreground mt-4">
              Operated by Zeta Aztra Technologies (Individual Proprietorship, India) • © 2025 Zeta Aztra Technologies. All Rights Reserved. • Jurisdiction: Chennai, Tamil Nadu • Contact: zetaaztratech@gmail.com • Version: v1.0.0
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
