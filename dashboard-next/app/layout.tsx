import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "V5.0 Ultra Dashboard",
  description: "Real-time AI Trading System",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased" suppressHydrationWarning>
        {children}
      </body>
    </html>
  );
}
