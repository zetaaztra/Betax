import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import { Link } from "wouter";

export default function About() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="mx-auto max-w-3xl px-6 py-12">
        <Link href="/">
          <a className="inline-flex items-center text-primary hover:underline mb-6 text-sm font-medium transition-colors">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Dashboard
          </a>
        </Link>
        <h1 className="text-3xl font-bold mb-2">About Tradyxa Aegis Matrix</h1>
        <p className="text-muted-foreground mb-8">Next-Day Forecasts, Volatility Analysis, and Quantitative ML Models</p>

        <div className="space-y-8">
          <section>
            <h2 className="text-xl font-semibold mb-3">Purpose</h2>
            <p className="text-muted-foreground leading-relaxed">
              Tradyxa Aegis Matrix is an educational platform designed to provide advanced options analytics, volatility indicators, and machine learning-based forecasts for NIFTY options trading. The dashboard aggregates real-time market data from NSE India and Yahoo Finance to compute various metrics including IV Rank, Volatility Risk Premium, Market Mood Index, and predictive models using Linear Regression, Logistic Regression, Random Forest, Quantile Regression, and LSTM neural networks.
            </p>
            <div className="mt-4 p-4 border border-yellow-500/20 bg-yellow-500/10 rounded-lg text-sm">
              <strong className="text-yellow-500">Important:</strong> This dashboard is for educational purposes only and does not constitute financial, investment, trading, or legal advice. All trading decisions are made at your own risk.
            </div>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3">Technology Stack</h2>
            <ul className="list-disc pl-5 space-y-2 text-muted-foreground">
              <li><strong>Frontend:</strong> Next.js 16, React 18, TypeScript, Tailwind CSS</li>
              <li><strong>Data Sources:</strong> NSE India API, Yahoo Finance</li>
              <li><strong>Analytics Engine:</strong> Python (pandas, numpy, scikit-learn, statsmodels, TensorFlow/Keras)</li>
              <li><strong>Machine Learning Models:</strong> Linear Regression, Logistic Regression, Random Forest, Quantile Regression, LSTM</li>
              <li><strong>Hosting:</strong> Cloudflare Pages</li>
              <li><strong>Advertising:</strong> Adsterra (adsterra.com)</li>
              <li><strong>Version:</strong> v1.0.0</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3">Data Sources & Attribution</h2>
            <ul className="list-disc pl-5 space-y-2 text-muted-foreground">
              <li><strong>NSE India:</strong> Real-time option chain data, historical prices</li>
              <li><strong>Yahoo Finance:</strong> Market data, VIX, historical OHLC data</li>
            </ul>
            <p className="text-muted-foreground mt-2 text-sm">
              Market data © respective owners. Tradyxa Aegis Matrix is unaffiliated with NSE or Yahoo. Market data may be delayed up to 30 minutes. For educational use only.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3">Legal & Privacy</h2>
            <ul className="list-disc pl-5 space-y-2 text-muted-foreground">
              <li><strong>Operated by:</strong> Zeta Aztra Technologies (Individual Proprietorship, India)</li>
              <li><strong>Jurisdiction:</strong> Chennai, Tamil Nadu, India</li>
              <li><strong>Contact:</strong> zetaaztratech@gmail.com</li>
              <li><strong>Version:</strong> v1.0.0</li>
            </ul>
            <p className="text-muted-foreground mt-4">
              <strong>Data Protection:</strong> This site does not collect or store any personally identifiable information. Server logs are automatically deleted within 7 days by the host (Cloudflare Pages).
            </p>
            <p className="text-muted-foreground mt-2">
              <strong>Advertising:</strong> This website displays advertisements provided by Adsterra (adsterra.com), a third-party advertising network. Adsterra may use cookies and similar technologies to deliver relevant ads. We do not control Adsterra's data collection practices.
            </p>
            <p className="text-muted-foreground mt-2">
              <strong>Intellectual Property:</strong> Visual models and code protected under Copyright Act, 1957 (India). Unauthorized use of the Tradyxa or Zeta Aztra name, logo, or visuals is strictly prohibited.
            </p>
          </section>

          <div className="pt-8 border-t border-border mt-8">
            <p className="text-sm text-muted-foreground italic">
              Affiliation Disclaimer: Tradyxa Aegis Matrix is a product of Zeta Aztra Technologies (India) and is not affiliated with any other Tradyxa-named companies or domains.
            </p>
            <p className="text-sm text-muted-foreground mt-4">
              For inquiries, support, or data deletion requests: <a href="mailto:zetaaztratech@gmail.com" className="underline hover:text-foreground">zetaaztratech@gmail.com</a>
            </p>
            <p className="text-sm text-muted-foreground mt-2">
              © 2025 Zeta Aztra Technologies. All Rights Reserved.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
