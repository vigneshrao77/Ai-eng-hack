import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "@/components/Navbar";

export const metadata: Metadata = {
  title: "ModernRx — AI-Powered Application Modernization Advisor",
  description:
    "GxP-aware modernization advisor for pharma IT: living architecture twin, GxP criticality scanner, blast-radius-aware decomposition, AI Architecture Council, and CSA assurance pack generator.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col bg-[var(--background)] text-[var(--foreground)] antialiased">
        <Navbar />
        <main className="flex-1 max-w-[1440px] w-full mx-auto px-8 py-8">
          {children}
        </main>
        <footer className="border-t border-[var(--border)] bg-[var(--surface-muted)] py-5 text-center text-xs text-[var(--ink-subtle)]">
          ModernRx &bull; Compliant with FDA CSA (2025/2026) &amp; EU GMP Annex 11 / Draft Annex 22 &bull; Draft Assurance Evidence (Requires QA Review)
        </footer>
      </body>
    </html>
  );
}
