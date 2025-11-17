import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "GhostSage – Personal AI Assistant",
  description:
    "Local personal AI assistant with FastAPI backend, RAG (ChromaDB), and Next.js frontend.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-slate-950 text-slate-100">{children}</body>
    </html>
  );
}
