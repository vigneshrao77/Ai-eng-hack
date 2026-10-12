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
    <html lang="en" className="dark">
      <body className="min-h-screen flex flex-col bg-black text-zinc-100 antialiased font-sans selection:bg-white selection:text-black">
        <Navbar />
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {children}
        </main>
        <footer className="border-t border-zinc-900 bg-black py-4 text-center text-xs text-zinc-500">
          ModernRx &bull; Compliant with FDA CSA (2025/2026) &amp; EU GMP Annex 11 / Draft Annex 22 &bull; Draft Assurance Evidence (Requires QA Review)
        </footer>
      </body>
    </html>
  );
}
