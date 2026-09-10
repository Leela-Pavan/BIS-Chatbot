import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "BIS Sahayak",
  description: "Evidence-first assistance for Indian Standards and BIS services.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
