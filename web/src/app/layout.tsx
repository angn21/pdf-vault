import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { PrivacyBadge } from "@/components/PrivacyBadge";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "PDF Vault — Self-Hosted PDF Toolkit",
  description:
    "Privacy-first, self-hosted PDF tools. Merge, split, compress, convert, and more — files never leave your machine.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} min-h-screen`}>
        <div className="min-h-screen flex flex-col">
          <header className="border-b border-vault-border bg-vault-card/50 backdrop-blur sticky top-0 z-50">
            <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
              <a href="/" className="flex items-center gap-3 group">
                <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-vault-accent to-vault-accent2 flex items-center justify-center text-sm font-bold">
                  PV
                </div>
                <div>
                  <div className="font-semibold tracking-tight group-hover:text-vault-accent2 transition-colors">
                    PDF Vault
                  </div>
                  <div className="text-xs text-vault-muted">Self-hosted · Private</div>
                </div>
              </a>
              <nav className="flex gap-4 text-sm text-vault-muted">
                <a href="/workflows" className="hover:text-white transition-colors">
                  Workflows
                </a>
              </nav>
            </div>
          </header>
          <main className="flex-1">{children}</main>
          <footer className="border-t border-vault-border py-6">
            <div className="max-w-6xl mx-auto px-4">
              <PrivacyBadge />
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
