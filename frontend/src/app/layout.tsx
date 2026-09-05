import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CapstoneAI — Your AI Project Mentor",
  description: "Generate award-winning final-year project ideas powered by AI",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="antialiased">
      <body className="min-h-screen bg-[#0a0a0a] text-white" style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif' }}>
        {children}
      </body>
    </html>
  );
}

