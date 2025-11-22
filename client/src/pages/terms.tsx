import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import { Link } from "wouter";

export default function Terms() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="mx-auto max-w-3xl px-6 py-12">
        <Link href="/">
          <a className="inline-flex items-center text-primary hover:underline mb-6 text-sm font-medium transition-colors">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Dashboard
          </a>
        </Link>
        <h1 className="text-3xl font-bold mb-2">Terms of Use</h1>
        <p className="text-muted-foreground mb-8">User obligations, acceptable use, and legal terms</p>

        <div className="space-y-8">
          <section>
            <h2 className="text-xl font-semibold mb-3">Acceptance</h2>
            <p className="text-muted-foreground leading-relaxed">
              By accessing or using this website, you agree to these Terms, the Privacy Policy, Cookie Notice, and Disclaimer. If you do not agree, do not use the site.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3">No Advice</h2>
            <p className="text-muted-foreground leading-relaxed">
              The site provides educational and informational content only. We do not provide investment advice. You acknowledge sole responsibility for your trading/investment actions.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3">Intellectual Property</h2>
            <p className="text-muted-foreground leading-relaxed">
              © 2025 Zeta Aztra Technologies. All rights reserved. All code, models, visualizations, and branding are protected under applicable laws, including the Indian Copyright Act, 1957. Unauthorized reproduction, scraping, framing, or redistribution is prohibited. "Tradyxa" and "Zeta Aztra" are brand identifiers; unauthorized use is prohibited.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3">Data Attribution</h2>
            <p className="text-muted-foreground leading-relaxed">
              Market data © respective owners. Tradyxa Aegis Matrix is not affiliated with NSE or Yahoo. Derived analytics and computed indicators are © Zeta Aztra Technologies. Market data may be delayed up to 30 minutes. For educational use only.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3">Acceptable Use</h2>
            <ul className="list-disc pl-5 space-y-2 text-muted-foreground">
              <li>No unlawful, abusive, or malicious use of the site or data.</li>
              <li>No automated scraping or bulk extraction of content without prior written consent.</li>
              <li>No reverse engineering of proprietary models or bypassing rate limits.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3">Jurisdiction & Contact</h2>
            <p className="text-muted-foreground leading-relaxed">
              These Terms are governed by the laws of India. All disputes are subject exclusively to the courts of Chennai, Tamil Nadu. Contact: zetaaztratech@gmail.com.
            </p>
          </section>

          <div className="pt-8 border-t border-border mt-8">
            <p className="text-sm text-muted-foreground italic">
              Affiliation Disclaimer: Tradyxa Aegis Matrix is a product of Zeta Aztra Technologies (India) and is not affiliated with any other Tradyxa-named companies or domains.
            </p>
            <p className="text-sm text-muted-foreground mt-4">
              Last updated: 21/11/2025
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
