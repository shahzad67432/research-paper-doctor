"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Compass } from "lucide-react";
import { DiscoveryCard } from "@/components/DiscoveryCard";
import { sendInterest, getJobStatus } from "@/lib/api";

export default function DiscoverPage() {
  const [interest, setInterest] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const poll = useCallback((id: string) => {
    intervalRef.current = setInterval(async () => {
      try {
        const status = await getJobStatus(id);
        if (status.status === "done") {
          if (intervalRef.current) clearInterval(intervalRef.current);
          setLoading(false);
          const result = status.result as Record<string, any> | undefined;
          const discoveries = (result?.discovery_results as any[]) || [];
          setResults(discoveries);
        } else if (status.status === "error") {
          if (intervalRef.current) clearInterval(intervalRef.current);
          setLoading(false);
          setError(status.error || "Discovery failed");
        }
      } catch {
        if (intervalRef.current) clearInterval(intervalRef.current);
        setLoading(false);
      }
    }, 1500);
  }, []);

  useEffect(() => {
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, []);

  const handleFind = useCallback(async () => {
    if (!interest.trim() || loading) return;
    setLoading(true);
    setResults(null);
    setError(null);
    try {
      const { job_id } = await sendInterest(interest);
      poll(job_id);
    } catch {
      setLoading(false);
      setError("Failed to send request.");
    }
  }, [interest, loading, poll]);

  return (
    <div className="p-6 max-w-5xl mx-auto">
      {/* Hero input */}
      <div className="flex flex-col items-center justify-center min-h-[40vh] text-center">
        <Compass size={40} className="text-text-muted mb-4" />
        <div className="w-full max-w-2xl">
          <input
            value={interest}
            onChange={(e) => setInterest(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleFind()}
            placeholder="Enter your research interest..."
            className="w-full bg-transparent text-center font-display text-3xl text-text-primary placeholder:text-text-muted border-none border-b border-border-subtle pb-3 focus:outline-none focus:border-accent transition-colors"
          />
          <div className="h-1 mt-1 flex justify-center">
            {interest === "" && (
              <span className="w-0.5 h-5 bg-accent animate-pulse" />
            )}
          </div>
        </div>
        <button
          onClick={handleFind}
          disabled={!interest.trim() || loading}
          className="mt-8 px-8 h-12 rounded-lg font-display font-semibold text-canvas bg-gradient-to-r from-accent to-accent-bright hover:brightness-110 hover:-translate-y-0.5 hover:shadow-[0_8px_24px_rgba(91,141,239,0.27)] transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:transform-none"
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <span className="w-4 h-4 border-2 border-canvas border-t-transparent rounded-full animate-spin" />
              Discovering...
            </span>
          ) : (
            "Find Gaps →"
          )}
        </button>
      </div>

      {/* Results */}
      <AnimatePresence>
        {loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-8"
          >
            <span className="text-text-secondary text-sm font-mono">
              Searching databases and analyzing with LLM...
            </span>
          </motion.div>
        )}

        {error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-8"
          >
            <p className="text-rose text-sm">{error}</p>
          </motion.div>
        )}

        {results !== null && !loading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            {results.length === 0 ? (
              <p className="text-center text-text-secondary text-sm py-12">
                No opportunities found yet — try a broader topic
              </p>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {results.map((item: any, i: number) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.05 }}
                  >
                    <DiscoveryCard item={item} />
                  </motion.div>
                ))}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
