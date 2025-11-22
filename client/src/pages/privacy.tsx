import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import { Link } from "wouter";

export default function Privacy() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="mx-auto max-w-3xl px-6 py-12">
        <Link href="/">
          <a className="inline-flex items-center text-primary hover:underline mb-6 text-sm font-medium transition-colors">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Dashboard
          </a>
        </Link>
        <h1 className="text-3xl font-bold mb-2">Privacy Policy</h1>
        <p className="text-muted-foreground mb-8">How we handle your data and protect your privacy</p>

        <div className="space-y-8">
          <section>
            <h2 className="text-xl font-semibold mb-3">Overview</h2>
            <p className="text-muted-foreground leading-relaxed">
              This website does not collect, store, or process personally identifiable information (PII). Tradyxa Aegis Matrix uses publicly available market data (e.g., Yahoo Finance, NSE India) and does not require user accounts or user-submitted data for access. Market data may be delayed up to 30 minutes. For educational use only.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3">Hosting & Logs</h2>
            <p className="text-muted-foreground leading-relaxed">
              The site is hosted by Cloudflare Pages (Cloudflare, Inc.). For security and performance, Cloudflare may process limited technical information such as IP address, user agent, and timestamps in server logs. We do not persist or export these logs. To the best of our knowledge, host logs are auto-purged within a short retention window (typically ≤ 7 days). We do not combine logs with any other data to identify individuals.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3">Analytics</h2>
            <p className="text-muted-foreground leading-relaxed">
              We may use anonymous, aggregate analytics (e.g., Cloudflare Analytics) for performance monitoring only. If Google Analytics is enabled, it will operate under Google Consent Mode v2 and respect your consent choices. IP anonymization is enabled where applicable.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3">Cookies</h2>
            <p className="text-muted-foreground leading-relaxed">
              We use minimal cookies for theme preferences (dark/light) and basic site functionality. Analytics and advertising cookies (if any) are used only with your consent. This website displays advertisements from Adsterra (adsterra.com), a third-party advertising network. Adsterra may use cookies and similar technologies to deliver relevant ads and measure ad performance. We do not control Adsterra's data collection practices. For more information about Adsterra's privacy practices, please visit their privacy policy. Users in the EEA/UK are shown a Google-certified CMP (Funding Choices) implementing IAB TCF v2.2. You can change your choices at any time via the Cookie Settings/Preferences link or banner.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3">International & Indian Compliance</h2>
            <ul className="list-disc pl-5 space-y-2 text-muted-foreground">
              <li><strong>India:</strong> Information Technology Act, 2000; SPDI Rules 2011; SEBI IA Regulations (not an adviser).</li>
              <li><strong>EU/UK:</strong> GDPR/UK-GDPR – lawful basis: legitimate interests and consent (where required).</li>
              <li><strong>California:</strong> CCPA/CPRA – we do not sell personal information.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3">Your Choices</h2>
            <p className="text-muted-foreground leading-relaxed">
              You may request removal of any retained technical data by contacting us. Provide a detailed description (date/time/region) so we can coordinate with our host. For cookie choices, use the Cookie Settings link above to review or modify consent.
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
