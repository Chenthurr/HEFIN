import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "HEFIN — Healthcare Financial Intelligence Network",
  description:
    "AI-native healthcare intelligence and accessibility platform.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
