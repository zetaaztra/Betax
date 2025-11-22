export function Footer() {
  return (
    <footer className="border-t border-border bg-card mt-auto">
      <div className="mx-auto max-w-7xl px-6 py-12">
        <div className="space-y-6 text-center">
          <div className="space-y-3 text-sm text-muted-foreground">
            <p>
              <strong className="text-foreground">Data Sources:</strong> NSE India, Yahoo Finance
            </p>
            <p>
              <strong className="text-foreground">Analytics powered by</strong> Tradyxa Analytics Engine v1.0.0
            </p>
            <p className="text-xs">
              Market data © respective owners. Tradyxa Aegis Matrix is unaffiliated with NSE or Yahoo.
            </p>
            <p className="text-xs">
              Market data may be delayed up to 30 minutes. <strong className="text-foreground">For educational use only.</strong>
            </p>
          </div>

          <div className="pt-6 border-t border-border space-y-3">
            <p className="text-sm text-muted-foreground">
              <strong className="text-foreground">Operated by Zeta Aztra Technologies</strong> (Individual Proprietorship, India)
            </p>
            <p className="text-xs text-muted-foreground">
              © 2025 Zeta Aztra Technologies. All Rights Reserved.
            </p>
            <p className="text-xs text-muted-foreground">
              <a href="mailto:zetaaztratech@gmail.com" className="hover:text-foreground underline">
                zetaaztratech@gmail.com
              </a>
              {" | "}
              Jurisdiction: Chennai, Tamil Nadu
              {" | "}
              Version: v1.0.0
            </p>
          </div>

          <div className="pt-6 border-t border-border space-y-3 text-xs text-muted-foreground">
            <p>
              Visual models and code protected under Copyright Act, 1957 (India).
              Unauthorized use of the Tradyxa or Zeta Aztra name, logo, or visuals is strictly prohibited.
            </p>
            <p>
              Tradyxa Aegis Matrix is a product of Zeta Aztra Technologies (India) and is not affiliated with any other Tradyxa-named companies or domains.
            </p>
          </div>

          <div className="flex flex-wrap justify-center gap-3 pt-4 text-xs">
            <a href="/privacy" className="hover:text-foreground underline" data-testid="link-privacy">
              Privacy Policy
            </a>
            <span>·</span>
            <a href="/cookies" className="hover:text-foreground underline" data-testid="link-cookies">
              Cookie Preferences
            </a>
            <span>·</span>
            <a href="/terms" className="hover:text-foreground underline" data-testid="link-terms">
              Terms of Use
            </a>
            <span>·</span>
            <a href="/disclaimer" className="hover:text-foreground underline" data-testid="link-disclaimer">
              Disclaimer
            </a>
            <span>·</span>
            <a href="/about" className="hover:text-foreground underline" data-testid="link-about">
              About
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
