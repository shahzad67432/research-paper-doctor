import type { Metadata } from "next";
import "./globals.css";
import { Sidebar } from "@/components/Sidebar";

export const metadata: Metadata = {
  title: "PaperDoctor AI — Research Paper Analyzer & Publication Optimizer",
  description:
    "Analyze research papers for gaps, check similarity against arXiv and PubMed, verify citations, and score publication readiness. Built with LangGraph, RAG, and Gemini.",
  keywords: [
    "research paper analyzer",
    "academic gap finder",
    "publication readiness",
    "citation verification",
    "NLP tool",
  ],
  openGraph: {
    title: "PaperDoctor AI",
    description: "Analyze research papers. Find gaps. Score readiness.",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="bg-canvas">
      <body className="font-body antialiased text-text-primary bg-canvas min-h-screen">
        <Sidebar />
        <main className="pl-60 min-h-screen">{children}</main>
      </body>
    </html>
  );
}
