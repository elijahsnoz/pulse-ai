import type { Metadata, Viewport } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "Pulse — The AI Second Screen for Every Football Match",
  description:
    "Pulse lets fans feel a football match, not just follow it. An AI companion that watches with you.",
};

export const viewport: Viewport = {
  themeColor: "#070b16",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">{children}</body>
    </html>
  );
}
