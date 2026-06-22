"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  FileText,
  MessageSquare,
  Compass,
  Activity,
  ExternalLink,
} from "lucide-react";
import { useEffect, useState } from "react";
import { getCacheStats } from "@/lib/api";

const nav = [
  { href: "/", label: "Analyze", icon: FileText },
  { href: "/qa", label: "Q&A", icon: MessageSquare },
  { href: "/discover", label: "Discover", icon: Compass },
  { href: "/pipeline", label: "Pipeline", icon: Activity },
];

export function Sidebar() {
  const pathname = usePathname();
  const [cachedCount, setCachedCount] = useState<number | null>(null);

  useEffect(() => {
    getCacheStats()
      .then((s) => setCachedCount(s.papers_cached))
      .catch(() => setCachedCount(null));
  }, []);

  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-60 bg-surface border-r border-border flex flex-col">
      {/* Logo */}
      <div className="flex items-center gap-3 px-6 pt-8 pb-6">
        <svg
          width="32"
          height="32"
          viewBox="0 0 32 32"
          fill="none"
          className="shrink-0"
        >
          <path
            d="M16 2L28 10V22L16 30L4 22V10L16 2Z"
            stroke="#5B8DEF"
            strokeWidth="1.5"
            fill="none"
          />
          <path
            d="M16 8L22 12V18L16 22L10 18V12L16 8Z"
            stroke="#5B8DEF"
            strokeWidth="1.5"
            fill="none"
            opacity="0.6"
          />
          <circle cx="16" cy="16" r="2" fill="#7BB3FF" />
        </svg>
        <span className="font-display font-semibold text-text-primary text-lg tracking-tight">
          PaperDoctor <span className="text-accent">AI</span>
        </span>
      </div>

      {/* Nav items */}
      <nav className="flex-1 px-3 space-y-1">
        {nav.map(({ href, label, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-all duration-150
                ${
                  active
                    ? "bg-surface-high text-text-primary border-l-2 border-accent"
                    : "text-text-secondary hover:text-text-primary hover:bg-surface-high"
                }`}
            >
              <Icon size={18} />
              {label}
            </Link>
          );
        })}
      </nav>

      {/* Bottom */}
      <div className="px-6 pb-6 space-y-4">
        <div className="border-t border-border pt-4">
          <div className="flex items-center justify-between text-xs font-mono text-text-secondary">
            <span>Papers cached</span>
            <span className="text-accent font-semibold">
              {cachedCount ?? "—"}
            </span>
          </div>
        </div>
        <a
          href="https://github.com/shahzad67432/research-paper-doctor"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 text-xs text-text-secondary hover:text-text-primary transition-colors"
        >
          <ExternalLink size={14} />
          GitHub
        </a>
      </div>
    </aside>
  );
}
