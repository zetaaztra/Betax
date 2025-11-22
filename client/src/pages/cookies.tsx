import { Button } from "@/components/ui/button";
import { Link } from "wouter";
import { ArrowLeft } from "lucide-react";

export default function Cookies() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="mx-auto max-w-3xl px-6 py-12">
        <Link href="/">
          <a className="inline-flex items-center text-primary hover:underline mb-6 text-sm font-medium transition-colors">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Dashboard
          </a>
        </Link>
        <h1 className="text-3xl font-bold mb-2">Cookie Notice</h1>
        <p className="text-muted-foreground mb-8">How we use cookies and manage your consent preferences</p>

        <div className="space-y-8">
          <section>
            <p className="text-muted-foreground leading-relaxed">
              We use a minimal set of cookies and similar technologies to operate this site. Some cookies are strictly necessary; others (analytics) are used only with your consent.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3">Cookie Categories</h2>
            <ul className="list-disc pl-5 space-y-2 text-muted-foreground">
              <li><strong>Strictly Necessary / Security:</strong> required for basic operation and security; always enabled.</li>
              <li><strong>Functionality:</strong> theme preference (dark/light), UI settings.</li>
              <li><strong>Analytics:</strong> anonymized traffic/performance metrics (enabled only with consent).</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3">Consent Management</h2>
            <p className="text-muted-foreground leading-relaxed">
              We provide a consent banner to manage your preferences. Your choices are stored locally in your browser and will persist until you change them or clear your browser data.
            </p>
            <div className="mt-4">
              <Button variant="outline" onClick={() => document.dispatchEvent(new CustomEvent('open-cookie-settings'))}>
                Open Cookie Settings
              </Button>
            </div>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3">Third Parties</h2>
            <ul className="list-disc pl-5 space-y-2 text-muted-foreground">
              <li><strong>Cloudflare Pages:</strong> hosting and performance; may log IPs for security.</li>
              <li><strong>Adsterra:</strong> third-party advertising network (adsterra.com); may use cookies for ad delivery and measurement. We do not control Adsterra's data collection practices.</li>
              <li><strong>Optional Google Analytics:</strong> anonymized analytics with Consent Mode v2.</li>
            </ul>
          </section>

          <div className="pt-8 border-t border-border mt-8">
            <p className="text-sm text-muted-foreground italic">
              Affiliation Disclaimer: Tradyxa Aegis Matrix is a product of Zeta Aztra Technologies (India) and is not affiliated with any other Tradyxa-named companies or domains.
            </p>
            <p className="text-sm text-muted-foreground mt-4">
              Contact: <a href="mailto:zetaaztratech@gmail.com" className="underline hover:text-foreground">zetaaztratech@gmail.com</a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
