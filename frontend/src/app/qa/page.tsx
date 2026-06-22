"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, BookOpen } from "lucide-react";
import { sendQuery, getJobStatus } from "@/lib/api";

const EXAMPLES = [
  "What methods work for NLP in low-resource languages?",
  "How do transformer models handle long documents?",
  "What are the main gaps in federated learning research?",
];

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  papers?: Array<{ title: string; year: number; url: string }>;
  api_calls_saved?: number;
}

export default function QAPage() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const poll = useCallback((id: string) => {
    intervalRef.current = setInterval(async () => {
      try {
        const status = await getJobStatus(id);
        if (status.status === "done") {
          if (intervalRef.current) clearInterval(intervalRef.current);
          setLoading(false);
          const result = status.result as Record<string, any> | undefined;
          const qa = result?.qa_result as Record<string, any> | undefined;
          if (qa) {
            setMessages((prev) => [
              ...prev,
              {
                id: `resp-${Date.now()}`,
                role: "assistant",
                content: qa.answer || "No answer generated.",
                papers: qa.papers_used,
                api_calls_saved: qa.api_calls_saved,
              },
            ]);
          }
        } else if (status.status === "error") {
          if (intervalRef.current) clearInterval(intervalRef.current);
          setLoading(false);
          setMessages((prev) => [
            ...prev,
            {
              id: `err-${Date.now()}`,
              role: "assistant",
              content: `Error: ${status.error || "Request failed"}`,
            },
          ]);
        }
      } catch {
        if (intervalRef.current) clearInterval(intervalRef.current);
        setLoading(false);
      }
    }, 1500);
  }, []);

  useEffect(() => {
    const id = intervalRef.current;
    return () => {
      if (id) clearInterval(id);
    };
  }, []);

  const handleSend = useCallback(async () => {
    if (!query.trim() || loading) return;
    const q = query.trim();
    setQuery("");
    setMessages((prev) => [
      ...prev,
      { id: `q-${Date.now()}`, role: "user", content: q },
    ]);
    setLoading(true);
    try {
      const { job_id } = await sendQuery(q);
      poll(job_id);
    } catch {
      setLoading(false);
      setMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          role: "assistant",
          content: "Failed to send query. Check API connection.",
        },
      ]);
    }
  }, [query, loading, poll]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const autoResize = () => {
    const ta = textareaRef.current;
    if (ta) {
      ta.style.height = "auto";
      ta.style.height = Math.min(ta.scrollHeight, 120) + "px";
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-0px)]">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 max-w-3xl mx-auto w-full">
        <AnimatePresence>
          {messages.length === 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex flex-col items-center justify-center h-full text-center"
            >
              <BookOpen size={48} className="text-text-muted" />
              <h2 className="font-display text-xl text-text-secondary mt-4">
                Ask anything about research
              </h2>
              <div className="flex flex-wrap gap-2 mt-6 max-w-md justify-center">
                {EXAMPLES.map((ex) => (
                  <button
                    key={ex}
                    onClick={() => setQuery(ex)}
                    className="px-3 py-1.5 rounded-full border border-border text-xs text-text-secondary hover:text-text-primary hover:border-accent transition-colors"
                  >
                    {ex}
                  </button>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        {messages.map((msg) => (
          <motion.div
            key={msg.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] rounded-2xl p-4 ${
                msg.role === "user"
                  ? "bg-accent/20 border border-accent/40 text-text-primary"
                  : "bg-surface-high border border-border-subtle text-text-primary"
              }`}
            >
              <p className="text-sm whitespace-pre-wrap leading-relaxed">{msg.content}</p>
              {msg.papers && msg.papers.length > 0 && (
                <div className="mt-3 pt-3 border-t border-border-subtle">
                  <p className="text-xs text-text-secondary font-mono mb-2">
                    Papers Referenced
                  </p>
                  <div className="flex gap-2 overflow-x-auto pb-1">
                    {msg.papers.map((p, i) => (
                      <div
                        key={i}
                        className="shrink-0 bg-surface border border-border rounded-lg px-3 py-2 min-w-[140px]"
                      >
                        <p className="text-xs text-text-primary truncate">{p.title}</p>
                        <p className="text-[10px] text-text-secondary">{p.year}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              {msg.api_calls_saved !== undefined && msg.api_calls_saved > 0 && (
                <p className="mt-2 text-xs text-mint font-mono">
                  ✓ {msg.api_calls_saved} results from cache · 0 API calls
                </p>
              )}
            </div>
          </motion.div>
        ))}
        {loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex justify-start"
          >
            <div className="bg-surface-high border border-border-subtle rounded-2xl p-4">
              <span className="flex items-center gap-2 text-sm text-text-secondary">
                <span className="w-3 h-3 border-2 border-accent border-t-transparent rounded-full animate-spin" />
                Searching papers...
              </span>
            </div>
          </motion.div>
        )}
      </div>

      {/* Input area */}
      <div className="sticky bottom-0 bg-canvas border-t border-border p-4">
        <div className="max-w-3xl mx-auto flex gap-3 items-end">
          <div className="flex-1 bg-surface-high border border-border rounded-2xl px-4 py-3 focus-within:border-accent transition-colors">
            <textarea
              ref={textareaRef}
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                autoResize();
              }}
              onKeyDown={handleKeyDown}
              placeholder="Ask about research methods, gaps in literature, what to read..."
              rows={1}
              className="w-full bg-transparent text-text-primary font-body placeholder:text-text-muted resize-none outline-none text-sm"
            />
          </div>
          <button
            onClick={handleSend}
            disabled={!query.trim() || loading}
            className="p-3 rounded-xl bg-accent text-canvas hover:brightness-110 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <Send size={18} />
          </button>
        </div>
        <p className="text-center mt-2 font-mono text-xs text-text-muted">
          Searches your cached paper corpus · No new API calls if cached
        </p>
      </div>
    </div>
  );
}
